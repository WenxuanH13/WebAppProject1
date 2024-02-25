import socketserver
from util.request import Request
from pymongo import MongoClient
import json
import html



class MyTCPHandler(socketserver.BaseRequestHandler):

    mongo_client = MongoClient("database") 
    db = mongo_client["cse312"] 
    chat_collection = db["chat"]
    messageID = 0

    def handle(self):
        allMessage = list(self.chat_collection.find({}, {"_id":0, "message": 1, "username": 1, "id": 1}))
        lastMessage = allMessage[len(allMessage) - 1]
        self.messageID = int(lastMessage['id'])

        received_data = self.request.recv(2048)
        print(self.client_address)
        print("--- received data ---")
        #print(received_data)
        print("--- end of data ---\n\n")
        request = Request(received_data)
        #print(request.path)

        # TODO: Parse the HTTP request and use self.request.sendall(response) to send your response
        pictures = {
            'public/image/cat.jpg',
            'public/image/dog.jpg',
            'public/image/eagle.jpg',
            'public/image/elephant-small.jpg',
            'public/image/elephant.jpg',
            'public/image/flamingo.jpg',
            'public/image/kitten.jpg'
        }
        allFilesPath = {
            'public/image/cat.jpg',
            'public/image/dog.jpg',
            'public/image/eagle.jpg',
            'public/image/elephant-small.jpg',
            'public/image/elephant.jpg',
            'public/image/flamingo.jpg',
            'public/image/kitten.jpg',
            'public/favicon.ico',
            'public/functions.js',
            '/',
            'public/style.css',
            'public/webrtc.js'
        }
        if request.path == '/chat-messages':
            if request.method == 'GET':
                self.request.sendall(self.send_chatGET())
                return
            elif request.method == "POST":
                self.request.sendall(self.send_store_chatPOST(request))
                return
        if request.path.startswith('/chat-messages/'):
            print(1)
            if request.method == 'GET':
                if self.check_message_exist(request) == True:
                    self.request.sendall(self.send_chatGET_Specific(request))
                    return
                else:
                    print(2)
                    self.request.sendall(self.generate404())
                    return
            elif request.method == 'POST':
                self.request.sendall(self.send_store_chatPOST(request))
                return

        #LO2 start
        if request.path == '/':
            servePath = '/'
        else:
            servePath = request.path[1:]
        if not servePath in allFilesPath:
            self.request.sendall(self.generate404())
            return
        if servePath in pictures:
            self.request.sendall(self.sendImageResponse(servePath))
            return
        if servePath == 'public/favicon.ico':
            self.request.sendall(self.sendFaviconResponse())
            return
        if servePath == 'public/functions.js':
            self.request.sendall(self.sendFunctionsResponse())
            return
        if servePath == '/':
            self.request.sendall(self.sendIndexResponse(request))
            return
        if servePath == 'public/style.css':
            self.request.sendall(self.sendStyleResponse())
            return
        if servePath == 'public/webrtc.js':
            self.request.sendall(self.sendWebrtcResponse())
            return

        

    def sendIndexResponse(self, request):
        if 'visits' in request.cookies:
            newCookies = {}
            for cookieKey in request.cookies.keys():
                newCookies[cookieKey] = request.cookies[cookieKey]
            newVisit = int(request.cookies.get("visits")) + 1
            maxAge = 3600
            newCookies["visits"] = str(newVisit)
            newCookies["Max-Age"] = str(maxAge)
            cookieHeader = ""
            for i, cookieKey2 in enumerate(newCookies):
                cookieHeader += cookieKey2 + '=' + newCookies[cookieKey2]
                if i < len(newCookies) - 1:
                    cookieHeader += "; "
        else:
            newCookies = {}
            for cookieKey in request.cookies.keys():
                newCookies[cookieKey] = request.cookies[cookieKey]
            firstVisit = 1
            maxAge = 3600
            newCookies["visits"] = str(firstVisit)
            newCookies["Max-Age"] = str(maxAge)
            cookieHeader = ""
            for i, cookieKey2 in enumerate(newCookies):
                cookieHeader += cookieKey2 + '=' + newCookies[cookieKey2]
                if i < len(newCookies) - 1:
                    cookieHeader += "; "

        status = "HTTP/1.1 200 OK\r\n"
        
        with open("public/index.html", 'r') as file:
            body = file.read()
            body = body.replace("{{visits}}", str(newCookies['visits']))
            body = body.replace("🙂", "&#128578")
            body = body.encode()
        headers = {
            "Content-Type": "text/html",
            "Content-Length": str(len(body)),
            "Set-Cookie" : cookieHeader,
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
    
    def sendStyleResponse(self):
        status = "HTTP/1.1 200 OK\r\n"
        with open("public/style.css", 'r') as file:
            body = file.read()
            body = body.encode()
        headers = {
            "Content-Type": "text/css",
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

    def sendWebrtcResponse(self):
        status = "HTTP/1.1 200 OK\r\n"
        with open("public/webrtc.js", 'r') as file:
            body = file.read()
            body = body.encode()
        headers = {
            "Content-Type": "text/javascript",
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
    
    def sendFunctionsResponse(self):
        status = "HTTP/1.1 200 OK\r\n"
        with open("public/functions.js", 'r') as file:
            body = file.read()
            body = body.replace("😀", "&#128512")
            body = body.encode()
        headers = {
            "Content-Type": "text/javascript",
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

    def sendFaviconResponse(self):
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

    def sendImageResponse(self,servepath):
        status = "HTTP/1.1 200 OK\r\n"
        with open(servepath, 'rb') as file:
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
        jsonDict = json.loads(request.body)
        message = html.escape(jsonDict["message"])
        self.messageID += 1
        dbMessage = {"message": message, "username": "Guest", "id":self.messageID}
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

    def send_chatGET(self):
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
        message = self.chat_collection.find_one({"id": int(requestedMessageID)}, {"_id":0, "message": 1, "username": 1, "id": 1})
        if message == None:
            return False
        else:
            return True
        
    def send_chatGET_Specific(self, request):
        requestedMessageID = request.path.split('/')[-1]
        message = self.chat_collection.find_one({"id": int(requestedMessageID)})
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

    def generate404(self):
        status = "HTTP/1.1 404 Not Found\r\n"
        body = "The requested content does not exist".encode()
        headers = {
            "Content-Type": "text/plain",
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


def main():
    host = "0.0.0.0"
    port = 8080

    socketserver.TCPServer.allow_reuse_address = True

    server = socketserver.TCPServer((host, port), MyTCPHandler)

    print("Listening on port " + str(port))

    server.serve_forever()


if __name__ == "__main__":
    main()
