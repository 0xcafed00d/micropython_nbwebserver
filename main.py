import network
import utime
import machine

import nbwebserver
from timeout import Timeout
import wifi_config

# ------------------------------------------------------------------------
# configure LED - pin number will be different on different boards
# ------------------------------------------------------------------------

led = machine.Pin(22, machine.Pin.OUT)
led.value(1)


# ------------------------------------------------------------------------
# connect to network
# ------------------------------------------------------------------------

timeout = Timeout(10000)

net = network.WLAN(network.STA_IF)
net.active(True)
net.connect(wifi_config.wifi_ssid, wifi_config.wifi_pw)

while not net.isconnected():
    led.value(not led.value())
    utime.sleep_ms(100)
    if timeout.hasExpired():
        machine.reset()

print(net.ifconfig())


# ------------------------------------------------------------------------
# start webserver
# ------------------------------------------------------------------------

# create webserver
server = nbwebserver.WebServer()

rate = 1000

# handler for /led requests


def ledHandler(request, response):
    print(request.header)
    print(request.query)
    response.sendOK()


# add handler to server
server.AddHandler("/led", ledHandler)

# start the server listening for connections
server.Start()

# loop forever updating webserver, and doing what else needs to be done

while True:
    server.Update()
    utime.sleep_ms(10)
    if timeout.hasExpired():
        timeout = Timeout(rate)
        led.value(not led.value())
