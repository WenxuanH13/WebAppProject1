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

        lines = decodeString.split('\r\n')
        requestLine = lines[0].split(' ')

        self.method = requestLine[0]
        self.path = requestLine[1]
        self.http_version = requestLine[2]

        for line in lines[1:]:
            if line == '':
                break
            part = line.split(':', 1)
            key = part[0]
            value = part[1].strip()
            self.headers[key] = value


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


if __name__ == '__main__':
    test1()
