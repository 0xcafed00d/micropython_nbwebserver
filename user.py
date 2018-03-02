import nbwebserver
import utime

server = nbwebserver.WebServer()


def lightsHandler(req, resp):
    print("lights handler", req.query)
    resp.sendResponse(200)


server.AddHandler("/light", lightsHandler)

server.Start()

while True:
    server.Update()
    utime.sleep_ms(10)
