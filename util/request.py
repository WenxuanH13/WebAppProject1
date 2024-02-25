class Request:

    def __init__(self, request: bytes):
        # TODO: parse the bytes of the request and populate the following instance variable  

        self.body = b""
        self.method = ""
        self.path = ""
        self.http_version = ""
        self.headers = {}
        self.cookies = {}

        decodeString = request.decode()
        #print(decodeString)

        lines = decodeString.split('\r\n')
        requestLine = lines[0].split(' ')

        self.method = requestLine[0]
        self.path = requestLine[1]
        self.http_version = requestLine[2]

        for line in lines[1:]:
            if line == '':
                break
            part = line.split(':', 1)
            key = part[0].strip()
            value = part[1].strip()
            self.headers[key] = value
            if key == "Cookie":
                cookiess = value.split(';')
                for cookie in cookiess:
                    cookiePart = cookie.split('=')
                    cookieKey = cookiePart[0].strip()
                    cookieVal = cookiePart[1].strip()
                    self.cookies[cookieKey] = cookieVal

        
        bodyIndex = decodeString.find('\r\n\r\n')
        if bodyIndex != -1:
            self.body = request[bodyIndex + len('\r\n\r\n'):]
        #print(self.path)
        
        
        

def test1():
    request = Request(b'GET / HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\n\r\n')
    assert request.method == "GET"
    assert "Host" in request.headers
    assert request.headers["Host"] == "localhost:8080"  # note: The leading space in the header value must be removed
    assert request.body == b""  # There is no body for this request.
    # When parsing POST requests, the body must be in bytes, not str

    # This is the start of a simple way (ie. no external libraries) to test your code.
    # It's recommended that you complete this test and add others, including at least one
    # test using a POST request. Also, ensure that the types of all values are correct

def test2():
    request = Request(b'POST / HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 5\r\n\r\nhello')
    assert request.method == "POST"
    assert "Content-Type" in request.headers
    assert request.headers["Content-Type"] == "text/plain"  # note: The leading space in the header value must be removed
    assert "Content-Length" in request.headers
    assert request.headers["Content-Length"] == "5" # note: The leading space in the header value must be removed
    assert request.body == b"hello"

def test3():
    request = Request(b'POST /test HTTP/1.1\r\nHost: foo.example\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: 27\r\n\r\nfield1=value1&field2=value2')
    assert request.method == "POST"
    assert request.path == "/test"
    assert request.http_version == "HTTP/1.1"
    assert "Host" in request.headers
    assert request.headers["Host"] == "foo.example"  # note: The leading space in the header value must be removed
    assert "Content-Type" in request.headers
    assert request.headers["Content-Type"] == "application/x-www-form-urlencoded"  # note: The leading space in the header value must be removed
    assert "Content-Length" in request.headers
    assert request.headers["Content-Length"] == "27" # note: The leading space in the header value must be removed
    assert request.body == b"field1=value1&field2=value2"


def test4():
    request = Request(b'POST /pathdaddas HTTP/1.1\r\nContent-Type: text/plain\r\nCookie: id=X6kAwpgW29M; visits=4; username=John; password=hi\r\nContent-Length: 10\r\n\r\nhellodasad')

if __name__ == '__main__':
    test1()
    test2()
    test3()
    test4()