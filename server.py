import base64
import socketserver
from util.request import Request
from pymongo import MongoClient
import json
import html
from util.router import Router
import bcrypt
import secrets
import util.auth
import hashlib
import requests
import os


class MyTCPHandler(socketserver.BaseRequestHandler):

    mongo_client = MongoClient("database") 
    db = mongo_client["cse312"] 
    chat_collection = db["chat"]
    user_account = db["accounts"]
    messageID = 0
    router = Router()
    
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    redirect_uri = os.getenv("REDIRECT_URI")
    

    def handle(self):
        self.route_setup()
        allMessage = list(self.chat_collection.find({}, {'_id': 0}))
        if len(allMessage) == 0:
            #print("this worked and you did something")
            self.messageID = 0
        else:
            lastMessage = allMessage[len(allMessage) - 1]
            self.messageID = int(lastMessage['id'])

        received_data = self.request.recv(2048)
        print(self.client_address)
        print("--- received data ---")
        #print(received_data)
        print("--- end of data ---\n\n")
        request = Request(received_data)
        print(request.method)
        print(request.path)

        # TODO: Parse the HTTP request and use self.request.sendall(response) to send your response
        self.request.sendall(self.router.route_request(request))
        
        







    def route_setup(self):
        self.router.add_route("GET","^/$", self.sendIndexResponse)
        self.router.add_route("GET","^/public/style.css$", self.sendStyleResponse)
        self.router.add_route("GET","^/public/functions.js$", self.sendFunctionsResponse)
        self.router.add_route("GET","^/public/webrtc.js$", self.sendWebrtcResponse)
        self.router.add_route("GET","^/public/favicon.ico$", self.sendFaviconResponse)
        self.router.add_route("GET","^/public/image/eagle.jpg$", self.sendEagleImageResponse)
        self.router.add_route("GET","^/public/image/cat.jpg$", self.sendCatImageResponse)
        self.router.add_route("GET","^/public/image/dog.jpg$", self.sendDogImageResponse)
        self.router.add_route("GET","^/public/image/elephant-small.jpg$", self.sendElephantSmallImageResponse)
        self.router.add_route("GET","^/public/image/elephant.jpg$", self.sendElephantImageResponse)
        self.router.add_route("GET","^/public/image/flamingo.jpg$", self.sendFlamingoImageResponse)
        self.router.add_route("GET","^/public/image/kitten.jpg$", self.sendKittenImageResponse)
        self.router.add_route("GET","^/chat-messages$", self.send_chatGET)
        self.router.add_route("POST","^/chat-messages$", self.send_store_chatPOST)
        self.router.add_route("GET","^/chat-messages/.", self.send_chatGET_Specific)
        self.router.add_route("DELETE","^/chat-messages/.", self.sendDeleteMessage)
        self.router.add_route("PUT","^/chat-messages/.", self.sendPutMessage)
        self.router.add_route("POST","^/register$", self.sendRegisterResponse)
        self.router.add_route("POST","^/login$", self.sendLoginResponse)
        self.router.add_route("POST","^/logout$",self.sendLogoutResponse)
        self.router.add_route("POST","^/spotify$",self.login_with_spotify)
        self.router.add_route("GET","^/spotify?.*",self.authFlow)

    def sendIndexResponse(self, request):
        if 'visits' in request.cookies:
            visits = int(request.cookies.get("visits")) + 1
        else:
            visits = 1
        
        with open("public/index.html", 'r') as file:
            body = file.read()
            body = body.replace("{{visits}}", str(visits))
            #body = body.replace("🙂", "&#128578")
            #body = body.encode()

        encoded = False
        if "auth_token" in request.cookies:
            token = request.cookies["auth_token"]
            hashed_token = hashlib.sha256(token.encode()).hexdigest()
            account = self.user_account.find_one({"hashed_token": hashed_token})
            if account != None:
                if "xsrf_token" not in account:
                    xsrf_token = secrets.token_hex(16)
                    self.user_account.update_one({"_id": account["_id"]}, {"$set": {"xsrf_token": xsrf_token}})
                else:
                    xsrf_token = account["xsrf_token"]
                
                body = body.replace("{{INSERT TOKEN}}", xsrf_token)
                
                index = body.find('"/login"') + len('"/login"')
                body = body[:index] + " hidden " + body[index:]
                index = body.find('"/register"') + len('"/register"')
                body = body[:index] + " hidden " + body[index:]
                index = body.find('"/spotify"') + len('"/spotify"')
                body = body[:index] + " hidden " + body[index:]
                body = body.encode()
                encoded = True
        else:
            
            index = body.find('"/logout"') + len('"/logout"')
            body = body[:index] + " hidden " + body[index:]
            body = body.encode()
            encoded = True

        if encoded == False:
            body = body.encode()


        status = "HTTP/1.1 200 OK\r\n"
        
        headers = {
            "Content-Type": "text/html; charset=UTF-8",
            "Content-Length": str(len(body)),
            "Set-Cookie" : f"visits={visits}; Max-Age=3600",
            "X-Content-Type-Options": "nosniff" 
        }
        responseHeader = ""
        for key, value in headers.items():
            responseHeader += key + ": " + value + "\r\n"
        responseHeader += "\r\n"
        response = status + responseHeader
        response = response.encode()
        response += body
        #print(request.cookies)
        return response

    def sendStyleResponse(self,request):
        status = "HTTP/1.1 200 OK\r\n"
        with open("public/style.css", 'r') as file:
            body = file.read()
            body = body.encode()
        headers = {
            "Content-Type": "text/css; charset=UTF-8",
            "Content-Length": str(len(body)),
            "X-Content-Type-Options": "nosniff" 
        }
        responseHeader = ""
        for key, value in headers.items():
            responseHeader += key + ": " + value + "\r\n"
        responseHeader += "\r\n"
        response = status + responseHeader
        response = response.encode()
        response += body
        return response

    def sendWebrtcResponse(self,request):
        status = "HTTP/1.1 200 OK\r\n"
        with open("public/webrtc.js", 'r') as file:
            body = file.read()
            body = body.encode()
        headers = {
            "Content-Type": "text/javascript; charset=UTF-8",
            "Content-Length": str(len(body)),
            "X-Content-Type-Options": "nosniff" 
        }
        responseHeader = ""
        for key, value in headers.items():
            responseHeader += key + ": " + value + "\r\n"
        responseHeader += "\r\n"
        response = status + responseHeader
        response = response.encode()
        response += body
        return response

    def sendFunctionsResponse(self,request):
        status = "HTTP/1.1 200 OK\r\n"
        with open("public/functions.js", 'r') as file:
            body = file.read()
            #bodyBytes = body.decode()
            #body = body.replace("😀", "&#128512")
            body = body.encode()
        headers = {
            "Content-Type": "text/javascript; charset=UTF-8",
            "Content-Length": str(len(body)),
            "X-Content-Type-Options": "nosniff" 
        }
        responseHeader = ""
        for key, value in headers.items():
            responseHeader += key + ": " + value + "\r\n"
        responseHeader += "\r\n"
        response = status + responseHeader
        response = response.encode()
        response += body
        return response

    def sendFaviconResponse(self,request):
        status = "HTTP/1.1 200 OK\r\n"
        with open("public/favicon.ico", 'rb') as file:
            body = file.read()
        headers = {
            "Content-Type": "image/x-icon",
            "Content-Length": str(len(body)),
            "X-Content-Type-Options": "nosniff" 
        }
        responseHeader = ""
        for key, value in headers.items():
            responseHeader += key + ": " + value + "\r\n"
        responseHeader += "\r\n"
        response = status + responseHeader
        response = response.encode()
        response += body
        return response 

    def sendCatImageResponse(self,request):
        status = "HTTP/1.1 200 OK\r\n"
        with open('public/image/cat.jpg', 'rb') as file:
            body = file.read()
        headers = {
            "Content-Type": "image/jpeg",
            "Content-Length": str(len(body)),
            "X-Content-Type-Options": "nosniff" 
        }
        responseHeader = ""
        for key, value in headers.items():
            responseHeader += key + ": " + value + "\r\n"
        responseHeader += "\r\n"
        response = status + responseHeader
        response = response.encode()
        response += body
        return response 
    
    def sendDogImageResponse(self,request):
        status = "HTTP/1.1 200 OK\r\n"
        with open('public/image/dog.jpg', 'rb') as file:
            body = file.read()
        headers = {
            "Content-Type": "image/jpeg",
            "Content-Length": str(len(body)),
            "X-Content-Type-Options": "nosniff" 
        }
        responseHeader = ""
        for key, value in headers.items():
            responseHeader += key + ": " + value + "\r\n"
        responseHeader += "\r\n"
        response = status + responseHeader
        response = response.encode()
        response += body
        return response 

    def sendEagleImageResponse(self,request):
        status = "HTTP/1.1 200 OK\r\n"
        with open('public/image/eagle.jpg', 'rb') as file:
            body = file.read()
        headers = {
            "Content-Type": "image/jpeg",
            "Content-Length": str(len(body)),
            "X-Content-Type-Options": "nosniff" 
        }
        responseHeader = ""
        for key, value in headers.items():
            responseHeader += key + ": " + value + "\r\n"
        responseHeader += "\r\n"
        response = status + responseHeader
        response = response.encode()
        response += body
        return response 

    def sendElephantSmallImageResponse(self,request):
        status = "HTTP/1.1 200 OK\r\n"
        with open('public/image/elephant-small.jpg', 'rb') as file:
            body = file.read()
        headers = {
            "Content-Type": "image/jpeg",
            "Content-Length": str(len(body)),
            "X-Content-Type-Options": "nosniff" 
        }
        responseHeader = ""
        for key, value in headers.items():
            responseHeader += key + ": " + value + "\r\n"
        responseHeader += "\r\n"
        response = status + responseHeader
        response = response.encode()
        response += body
        return response 

    def sendElephantImageResponse(self,request):
        status = "HTTP/1.1 200 OK\r\n"
        with open('public/image/elephant.jpg', 'rb') as file:
            body = file.read()
        headers = {
            "Content-Type": "image/jpeg",
            "Content-Length": str(len(body)),
            "X-Content-Type-Options": "nosniff" 
        }
        responseHeader = ""
        for key, value in headers.items():
            responseHeader += key + ": " + value + "\r\n"
        responseHeader += "\r\n"
        response = status + responseHeader
        response = response.encode()
        response += body
        return response 

    def sendFlamingoImageResponse(self,request):
        status = "HTTP/1.1 200 OK\r\n"
        with open('public/image/flamingo.jpg', 'rb') as file:
            body = file.read()
        headers = {
            "Content-Type": "image/jpeg",
            "Content-Length": str(len(body)),
            "X-Content-Type-Options": "nosniff" 
        }
        responseHeader = ""
        for key, value in headers.items():
            responseHeader += key + ": " + value + "\r\n"
        responseHeader += "\r\n"
        response = status + responseHeader
        response = response.encode()
        response += body
        return response 

    def sendKittenImageResponse(self,request):
        status = "HTTP/1.1 200 OK\r\n"
        with open('public/image/kitten.jpg', 'rb') as file:
            body = file.read()
        headers = {
            "Content-Type": "image/jpeg",
            "Content-Length": str(len(body)),
            "X-Content-Type-Options": "nosniff" 
        }
        responseHeader = ""
        for key, value in headers.items():
            responseHeader += key + ": " + value + "\r\n"
        responseHeader += "\r\n"
        response = status + responseHeader
        response = response.encode()
        response += body
        return response 
    
    def send_store_chatPOST(self,request):

        data = json.loads(request.body)
        xsrf_token = data.get("xsrf_token")
        #print(data)
        username = "Guest"
        message = html.escape(data["message"])
        if "auth_token" in request.cookies:
            token = request.cookies["auth_token"]
            hashed_token = hashlib.sha256(token.encode()).hexdigest()
            account = self.user_account.find_one({"hashed_token": hashed_token})
            if account != None:
                #print("it came here")
                if account["xsrf_token"] == xsrf_token:
                    username = account["username"]
                    if "access_token" in account:
                        message += self.getMusic(account["access_token"])
                else:
                    
                    return self.generate403(request)
                
        self.messageID += 1
        dbMessage = {"message": message,"username": username,"id": self.messageID}

        self.chat_collection.insert_one(dbMessage)
        dbMessage.pop("_id")
        body = json.dumps(dbMessage)
        status = "HTTP/1.1 201 Created\r\n"
        headers = {
            "Content-Type": "application/json",
            "Content-Length": str(len(body)),   
            "X-Content-Type-Options": "nosniff" 
        }
        responseHeader = ""
        for key, value in headers.items():
            responseHeader += key + ": " + value + "\r\n"
        responseHeader += "\r\n"
        response = status + responseHeader
        response += body
        response = response.encode()
        return response

    def send_chatGET(self,request):
        status = "HTTP/1.1 200 OK\r\n"
        allMessage = self.chat_collection.find({})
        body = []
        for entry in allMessage:
            newDict = {}
            newDict["message"] = entry["message"]
            newDict["username"] = entry["username"]
            newDict["id"] = entry["id"]
            body.append(newDict) 
        
        body = json.dumps(body)
        headers = {
            "Content-Type": "application/json",
            "Content-Length": str(len(body)),
            "X-Content-Type-Options": "nosniff" 
        }
        responseHeader = ""
        for key, value in headers.items():
            responseHeader += key + ": " + value + "\r\n"
        responseHeader += "\r\n"
        response = status + responseHeader
        response += body
        response = response.encode()
        
        return response

    def check_message_exist(self, request):
        requestedMessageID = request.path.split('/')[-1]
        message = self.chat_collection.find_one({"id": int(requestedMessageID)})
        if message == None:
            return False
        else:
            return True
        
    def send_chatGET_Specific(self, request):
        specificID = request.path.split('/')[-1]
        message = self.chat_collection.find_one({"id": int(specificID)})
        if(message == None):
            return self.generate404(request)
        
        # requestedMessageID = request.path.split('/')[-1]
        # message = self.chat_collection.find_one({"id": int(requestedMessageID)})
        body = {}
        body["message"] = message["message"]
        body["username"] = message["username"]
        body["id"] = message["id"]
        body = json.dumps(body)
        status = "HTTP/1.1 200 OK\r\n"
        headers = {
            "Content-Type": "application/json",
            "Content-Length": str(len(body)),
            "X-Content-Type-Options": "nosniff" 
        }
        responseHeader = ""
        for key, value in headers.items():
            responseHeader += key + ": " + value + "\r\n"
        responseHeader += "\r\n"
        response = status + responseHeader
        response += body
        response = response.encode()
        
        return response

    def sendDeleteMessage(self, request):
        theMessageID = request.path.split('/')[-1]
        message = self.chat_collection.find_one({"id": int(theMessageID)})
        if(message == None):
            return self.generate404(request)
        username = "Guest"
        if "auth_token" in request.cookies:
            token = request.cookies["auth_token"]
            hashed_token = hashlib.sha256(token.encode()).hexdigest()
            account = self.user_account.find_one({"hashed_token": hashed_token})
            username = account["username"]
        
        if username == message["username"]:
            self.chat_collection.delete_one({"id": int(theMessageID)})
            response = request.http_version
            response += " 204 No Content\r\n"
            response += "X-Content-Type-Options: nosniff\r\n"
            response +="Content-Length: " + "0" + "\r\n\r\n" 
            return response.encode()
        else:
            return self.generate403(request)

    def sendPutMessage(self, request):
        requestedMessageID = request.path.split('/')[-1]
        existence = self.chat_collection.find_one({"id": requestedMessageID})
        if existence is None:
            return self.generate404()
        
        newMessage = json.loads(request.body)
        updateMessage = {
            "$set": {
            "message":html.escape(newMessage["message"]),
            "username":html.escape(newMessage["username"])
            }
        }
        self.chat_collection.update_one({"id":int(requestedMessageID)},updateMessage)
        message = self.chat_collection.find_one({"id": requestedMessageID})
        message.pop("_id")
        body = json.dumps(message)
        status = "HTTP/1.1 200 OK\r\n"
        headers = {
            "Content-Type": "application/json",
            "Content-Length": str(len(body)),
            "X-Content-Type-Options": "nosniff" 
        }
        responseHeader = ""
        for key, value in headers.items():
            responseHeader += key + ": " + value + "\r\n"
        responseHeader += "\r\n"
        response = status + responseHeader
        response += body
        response = response.encode()
        
        return response

    def sendRegisterResponse(self, request):
        
        credential = util.auth.extract_credentials(request)
        
        if util.auth.validate_password(credential[1]) == True:
            encoded_password = credential[1].encode('utf-8')
            salt = bcrypt.gensalt(rounds=16)
            hashed_password = bcrypt.hashpw(encoded_password,salt)
            #print(hashed_password)
            data = {"username": credential[0],"salt": salt, "hash": hashed_password}
            self.user_account.insert_one(data)
            status = request.http_version + " 302 Found redirect\r\n"
            headers = {
                "Content-Type": "text/html",
                "X-Content-Type-Options": "nosniff",
                "Content-Length": "0",
                "Location": "/"
            }
            responseHeader = ""
            for key, value in headers.items():
                responseHeader += key + ": " + value + "\r\n"
            responseHeader += "\r\n"
            response = status + responseHeader
            response = response.encode()
            return response
        else:
            return self.generate404(request)

    def sendLoginResponse(self,request):
        credential = util.auth.extract_credentials(request)
        account = self.user_account.find_one({"username": credential[0]})
        #print(account)
        if account == None:
            return self.generate404(request)
        else:
            encoded_password = credential[1].encode('utf-8')
            salt = account["salt"]
            hashed = bcrypt.hashpw(encoded_password,salt)
            #print(str(hashed))
            if(hashed == account["hash"]):
                token = secrets.token_hex(16)
                hashed_token = hashlib.sha256(token.encode()).hexdigest()
                self.user_account.update_one({"_id": account["_id"]}, {"$set": {"hashed_token": hashed_token}})
                response = request.http_version
                response += " 302 Found redirect\r\n"
                response +="Content-Type: text/html\r\n"
                response += "X-Content-Type-Options: nosniff\r\n"
                response +="Content-Length: 0" + "\r\n"
                response += "Set-Cookie: auth_token=" + str(token) + "; Max-Age=3600; HttpOnly\r\n"
                response += "Location: /\r\n\r\n"
                return response.encode()
            else:
                return self.generate404(request)

    def generate404(self,request):
        status = "HTTP/1.1 404 Not Found\r\n"
        body = "The requested content does not exist".encode()
        headers = {
            "Content-Type": "text/plain; charset=UTF-8",
            "Content-Length": str(len(body)),
            "X-Content-Type-Options": "nosniff" 
        }
        responseHeader = ""
        for key, value in headers.items():
            responseHeader += key + ": " + value + "\r\n"
        responseHeader += "\r\n"
        response = status + responseHeader
        response = response.encode()
        response += body
        return response

    def generate403(self,request):
        status = request.http_version + " 403 Forbidden\r\n"
        body = "Forbidden Action".encode()
        headers = {
            "Content-Type": "text/plain; charset=UTF-8",
            "Content-Length": str(len(body)),
            "X-Content-Type-Options": "nosniff" 
        }
        responseHeader = ""
        for key, value in headers.items():
            responseHeader += key + ": " + value + "\r\n"
        responseHeader += "\r\n"
        response = status + responseHeader
        response = response.encode()
        response += body
        return response
    
    def sendLogoutResponse(self,request):
        if "auth_token" in request.cookies:
            token = request.cookies["auth_token"]
            hashed_token = hashlib.sha256(token.encode()).hexdigest()
            self.user_account.update_one({"hashed_token": hashed_token}, {"$unset": {"hashed_token": ""}})
        
        status = request.http_version + " 302 Found redirect\r\n"
        response = status
        response += "Content-Type: text/html\r\n"
        response += "Content-Length: 0" + "\r\n"
        response += "Set-Cookie: auth_token=; Max-Age=0; HttpOnly\r\n"
        response += "X-Content-Type-Options: nosniff\r\n"
        response += "Location: /\r\n\r\n"  
        return response.encode()

    def login_with_spotify(self,request):
        authorization_url = 'https://accounts.spotify.com/authorize?'
        authorization_params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': 'user-read-email user-read-private user-read-currently-playing'
        }
        url = requests.get(authorization_url,authorization_params).url

        response = request.http_version + " 302 Found redirect\r\n"
        response +="Content-Type: text/html\r\n"
        response += "X-Content-Type-Options: nosniff\r\n"
        response +="Content-Length: 0" + "\r\n"
        response += "Location: " + url + "\r\n\r\n"
        return response.encode()
    
    def authFlow(self, request):
        authCode = request.path[14:]
        
        authHeader = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        data = {
            'grant_type': "authorization_code",
            'code': authCode,
            'redirect_uri': self.redirect_uri
        }

        headers = {
            'Authorization': f'Basic {authHeader}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response2 = requests.post('https://accounts.spotify.com/api/token', data=data, headers=headers)
        
        access_token = json.loads(response2.text)["access_token"]
        if access_token != None:
            email = self.getEmail(access_token)
        
        account = self.user_account.find_one({"username": email})
        token = secrets.token_hex(16)
        hashed_token = hashlib.sha256(token.encode()).hexdigest()

        if account == None:
            #print("creating account with spotify")
            data = {"username": email, "access_token": access_token, "hashed_token": hashed_token}
            self.user_account.insert_one(data)  
        else:
            #print("account with spotify exists")
            self.user_account.update_one({"_id": account["_id"]}, {"$set": {"access_token": access_token, "hashed_token" : hashed_token}})


        response = request.http_version
        response += " 302 Found redirect\r\n"
        response +="Content-Type: text/html\r\n"
        response += "X-Content-Type-Options: nosniff\r\n"
        response +="Content-Length: 0" + "\r\n"
        response += "Set-Cookie: auth_token=" + str(token) + "; Max-Age=3600; HttpOnly\r\n"
        response += "Location: /\r\n\r\n"
        return response.encode()
               
    def getEmail(self, access_token):
        profileURL = 'https://api.spotify.com/v1/me'

        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        response = requests.get(profileURL, headers=headers)
        if response.status_code == 200:
            data = response.json()
            email = data.get('email')
            return email
        else:
            return None

    def getMusic(self, access_token):
        url = 'https://api.spotify.com/v1/me/player/currently-playing'

        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        response = requests.get(url, headers=headers)

        string = " (Currently listening to: Nothing)"
        if response.status_code == 200:
            data = response.json()
            if data.get('is_playing'):
                song = data['item']['name']
                artist = data['item']['artists'][0]['name']
                string = " (Currently listening to: " + str(song) + " by " + str(artist)+ ")"
        
        return string





def main():
    host = "0.0.0.0"
    port = 8080

    socketserver.TCPServer.allow_reuse_address = True

    server = socketserver.TCPServer((host, port), MyTCPHandler)

    print("Listening on port " + str(port))

    server.serve_forever()


if __name__ == "__main__":
    main()
