import network
import utime
import machine

import nbwebserver
import wifi_config

# ------------------------------------------------------------------------
# configure LED - pin number will be different on different boards
# ------------------------------------------------------------------------

led = machine.Pin(22, machine.Pin.OUT)
led.value(1)


# ------------------------------------------------------------------------
# connect to network
# ------------------------------------------------------------------------

net = network.WLAN(network.STA_IF)
net.active(True)
net.connect(wifi_config.wifi_ssid, wifi_config.wifi_pw)

while not net.isconnected():
    utime.sleep_ms(100)

print(net.ifconfig())


# ------------------------------------------------------------------------
# start webserver
# ------------------------------------------------------------------------

# create webserver
server = nbwebserver.WebServer()


# handler for /led requests
def ledHandler(request, response):
    if request.query == "command=on":
        led.value(0)
    elif request.query == "command=off":
        led.value(1)
    response.sendOK()


# add handler to server
server.AddHandler("/led", ledHandler)

# start the server listening for connections
server.Start()

# loop forever updating webserver, and doing what else needs to be done
while True:
    server.Update()
    utime.sleep_ms(10)
