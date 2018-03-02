import network
import time
import machine

import wifi_config


net = network.WLAN(network.STA_IF)
net.active(True)
net.connect(wifi_config.wifi_ssid, wifi_config.wifi_pw)

while not net.isconnected():
    time.sleep_ms(100)

print(net.ifconfig())

import user
