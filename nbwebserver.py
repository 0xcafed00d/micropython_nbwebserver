import errno
import socket as socket
from timetools import CountdownTimer

_nberrors = [errno.ETIMEDOUT, errno.EAGAIN, errno.EINPROGRESS, 118, 119]


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


class Request:

    MODE_GOT_CONNECTION = 1
    MODE_GOT_REQUEST = 2
    MODE_GOT_HEADER = 3
    MODE_DONE = 4

    def __init__(self, sock, addr, handlers):
        self.sock = sock
        self.addr = addr
        self.handlers = handlers
        self.reqTimeout = CountdownTimer(1000)
        self.mode = Request.MODE_GOT_CONNECTION
        self.buffer = b''

    def _parseLine(self, line):
        print("line ", line)
        if len(line) == 0:
            self.mode = Request.MODE_DONE

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


class Response:
    pass
