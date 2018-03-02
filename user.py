import nbwebserver
import utime
import machine

server = nbwebserver.WebServer()

led = machine.Pin(22, machine.Pin.OUT)
led.value(1)


def lightsHandler(req, resp):
    print("lights handler", req.query)
    if req.query == "command=on":
        led.value(0)
    elif req.query == "command=off":
        led.value(1)
    resp.sendResponse(200)


server.AddHandler("/light", lightsHandler)

server.Start()

while True:
    server.Update()
    utime.sleep_ms(10)
