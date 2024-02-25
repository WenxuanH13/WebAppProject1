import socketserver
from util.request import Request


class MyTCPHandler(socketserver.BaseRequestHandler):

    
    def handle(self):
        received_data = self.request.recv(2048)
        print(self.client_address)
        print("--- received data ---")
        print(received_data)
        print("--- end of data ---\n\n")
        request = Request(received_data)
        print(request.path)

        # TODO: Parse the HTTP request and use self.request.sendall(response) to send your response
        if request.path == '/':
            servePath = "public/index.html"
            #print(request.cookies)
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
        else:
            servePath = request.path[1:]
            #print(servePath)

        mimeType = self.getMimeType(servePath)
        #print(mimeType)
        
        if mimeType is None:
            self.request.sendall(self.generate404())
            return
        
        if type(mimeType) == str:
            mimeTypeCategory = mimeType.split('/')[0]
            if mimeTypeCategory == "image":
                try:
                    with open(servePath, 'rb') as file:
                        content = file.read()
                except FileNotFoundError:
                    self.request.sendall(self.generate404())
                    return
            elif request.path == '/':
                try:
                    with open(servePath, 'r') as file:
                        content = file.read()
                        content = content.replace("{{visits}}", str(newCookies['visits']))
                        content = content.replace("🙂", "&#128578")
                        #print(content)
                        content = content.encode()
                except FileNotFoundError:
                    self.request.sendall(self.generate404())
                    return
            elif request.path == '/public/functions.js':
                try:
                    with open(servePath, 'r') as file:
                        content = file.read()
                        content = content.replace("😀", "&#128512")
                        #print(content)
                        content = content.encode()
                except FileNotFoundError:
                    self.request.sendall(self.generate404())
                    return
            else:
                try:
                    with open(servePath, 'r') as file:
                        content = file.read().encode()
                except FileNotFoundError:
                    self.request.sendall(self.generate404())
                    return
        
        status = request.http_version + ' 200 OK'
        headers = {
            "Content-Type": mimeType,
            "Content-Length": str(len(content)),
            "X-Content-Type-Options": "nosniff" 
        }
        #print(cookieHeader)
        if request.path == '/':
            headers["Set-Cookie"] = cookieHeader
        responseHeader = ""
        for header in headers.keys():
            responseHeader += header + ": " + headers[header] + "\r\n"
        responseNoBody= status + "\r\n" + responseHeader + "\r\n"
        response = responseNoBody.encode() + content
        print(servePath)
        print(str(len(content)))
        self.request.sendall(response)
        
    
    
    def getMimeType(self, filePath):
        mimeTypes = {
            ".txt": "text/plain",
            ".html": "text/html",
            ".css": "text/css",
            ".js": "application/javascript",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".mp4": "video/mp4",
            ".json": "application/json",
            ".ico": "image/x-icon"
        }
        fileExtention = filePath.split(".")[-1].lower()
        fileExtention = "." + fileExtention
        mimeType = mimeTypes.get(fileExtention)
        return mimeType
    
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
