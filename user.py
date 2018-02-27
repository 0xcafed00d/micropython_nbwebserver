import nbwebserver
import utime

server = nbwebserver.WebServer()


def lightsHandler(req, resp):
    pass


server.AddHandler("/lights", lightsHandler)


while True:
    server.Update()
    utime.sleep_ms(10)
