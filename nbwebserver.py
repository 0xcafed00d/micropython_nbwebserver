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
        self.httpMethods = [b'GET', b'PUT']
        self.activeRequests = []
        self.requestHandlers = {}

    def Start(self):
        self.listenSocket = socket.socket()
        self.listenSocket.setblocking(False)
        self.listenSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listenSocket.bind(self.listenAddr)
        self.listenSocket.listen(1)

    def Update(self):
        sock, addr, ok = _nb_accept(self.listenSocket)
        if ok:
            r = Request(sock, addr, self.requestHandlers)
            self.activeRequests.append(r)

        for r in self.activeRequests:
            r.Update()

    def AddHandler(self, path, handler):
        self.requestHandlers[path] = handler


class Request:
    def __init__(self, sock, addr, handlers):
        self.sock = sock
        self.addr = addr
        self.handlers = handlers
        self.reqTimeout =

    def Update(self):
        return
        pass


class Response:
    pass
