import errno
import utime
import usocket as socket

_nberrors = [errno.ETIMEDOUT, errno.EAGAIN, errno.EINPROGRESS, 118, 119]


class Timeout:
    def __init__(self, time_ms):
        self.duration_ms = time_ms
        self.start_time = utime.ticks_ms()

    def hasExpired(self):
        return utime.ticks_diff(utime.ticks_ms(), self.start_time) >= self.duration_ms


def _nb_accept(sock):
    try:
        s, addr = sock.accept()
        s.setblocking(False)
        return s, addr, True
    except OSError as err:
        if err.args[0] in _nberrors:
            return None, None, False
        raise


def _nb_recv(sock, size):
    try:
        data = sock.recv(size)
        return data, True
    except OSError as err:
        if err.args[0] in _nberrors:
            return None, False
        raise


def _nb_send(sock, data):
    try:
        sent = sock.send(data)
        return sent, True
    except OSError as err:
        if err.args[0] in _nberrors:
            return None, False
        raise


class WebServer:
    def __init__(self, port=80):
        self.listenAddr = socket.getaddrinfo('0.0.0.0', port)[0][-1]
        self.activeRequests = []
        self.requestHandlers = {}
        self.listenSocket = socket.socket()

    def Start(self):
        self.listenSocket.setblocking(False)
        self.listenSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listenSocket.bind(self.listenAddr)
        self.listenSocket.listen(1)

    def Update(self):
        sock, addr, ok = _nb_accept(self.listenSocket)
        if ok:
            r = Request(sock, addr, self.requestHandlers)
            self.activeRequests.append(r)

        for i in range(len(self.activeRequests)-1, -1, -1):
            if self.activeRequests[i].Update() == Request.MODE_DONE:
                del self.activeRequests[i]

    def AddHandler(self, path, handler):
        self.requestHandlers[path] = handler


class Response:
    def __init__(self, sock):
        self._sock = sock

    def sendResponse(self, code):
        s = "HTTP/1.0 {} {}\r\n\r\n".format(code, Response._codes.get(code))
        _nb_send(self._sock, s)

    def sendOK(self):
        self.sendResponse(200)

    _codes = {
        100: 'Continue',
        101: 'Switching Protocols',
        200: 'OK',
        201: 'Created',
        202: 'Accepted',
        203: 'Non-Authoritative Information',
        204: 'No Content',
        205: 'Reset Content',
        206: 'Partial Content',
        300: 'Multiple Choices',
        301: 'Moved Permanently',
        302: 'Found',
        303: 'See Other',
        304: 'Not Modified',
        305: 'Use Proxy',
        307: 'Temporary Redirect',
        400: 'Bad Request',
        401: 'Unauthorized',
        402: 'Payment Required',
        403: 'Forbidden',
        404: 'Not Found',
        405: 'Method Not Allowed',
        406: 'Not Acceptable',
        407: 'Proxy Authentication Required',
        408: 'Request Timeout',
        409: 'Conflict',
        410: 'Gone',
        411: 'Length Required',
        412: 'Precondition Failed',
        413: 'Request Entity Too Large',
        414: 'Request-URI Too Long',
        415: 'Unsupported Media Type',
        416: 'Requested Range Not Satisfiable',
        417: 'Expectation Failed',
        500: 'Internal Server Error',
        501: 'Not Implemented',
        502: 'Bad Gateway',
        503: 'Service Unavailable',
        504: 'Gateway Timeout',
        505: 'HTTP Version Not Supported',
    }


class Request:

    MODE_GOT_CONNECTION = 1
    MODE_GOT_REQUEST = 2
    MODE_GOT_HEADER = 3
    MODE_DONE = 4

    def __init__(self, sock, addr, handlers):
        self.sock = sock
        self.addr = addr
        self.handlers = handlers
        self.reqTimeout = Timeout(2000)
        self.mode = Request.MODE_GOT_CONNECTION
        self.buffer = b''
        self.header = {}
        self.method = None
        self.reqPath = None
        self.query = None

    def _handleRequest(self):
        print(self.method)
        print(self.reqPath)
        print(self.query)
        print(self.header)
        handler = self.handlers.get(self.reqPath)
        if handler is not None:
            handler(self, Response(self.sock))
        self.sock.close()
        self.mode = Request.MODE_DONE

    def _parseLine(self, line):
        print("line ", line)
        if self.mode == Request.MODE_GOT_CONNECTION:
            r = line.split()
            if len(r) == 3:
                self.method = r[0]
                reqParts = r[1].split('?')
                self.reqPath = reqParts[0]
                if len(reqParts) > 1:
                    self.query = reqParts[1]
            else:
                self.mode = Request.MODE_DONE

            self.mode = Request.MODE_GOT_REQUEST
        elif self.mode == Request.MODE_GOT_REQUEST:
            if len(line) == 0:
                self.mode = Request.MODE_GOT_HEADER
            else:
                h = line.split()
                self.header[h[0]] = h[1].strip()

        if self.mode == Request.MODE_GOT_HEADER:
            self._handleRequest()

    def Update(self):
        if self.reqTimeout.hasExpired():
            print("timeout")
            self.mode = Request.MODE_DONE
        else:
            data, ok = _nb_recv(self.sock, 64)
            if ok:
                self.buffer += data
                while True:
                    eol = self.buffer.find(b'\r\n')
                    if eol == -1:
                        break
                    self._parseLine(self.buffer[:eol].decode())
                    self.buffer = self.buffer[eol+2:]

        return self.mode
