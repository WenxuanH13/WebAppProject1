import re

class Router:
    def __init__(self):
      self.routes = []
    
    def add_route(self, httpMethod, pathPattern, handlingFunc):
      self.routes.append((httpMethod, pathPattern, handlingFunc))
    
    def route_request(self, request):
        for httpMethod, pathPattern, handlingFunc in self.routes:
            if httpMethod == request.method and re.match(pathPattern, request.path):
                return handlingFunc(request)
        #below is 404 response if there is no requested content found
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



    if __name__ == "__main__":
      pass