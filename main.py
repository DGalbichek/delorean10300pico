import json
import network
import machine
import socket

from time import sleep
from picozero import LED, pico_temp_sensor

with open('.env', 'r+') as f:
    CONFIG = json.load(f)

CIRCUITS = {
    'head': LED(1),
    'time': LED(9),
    'posi': LED(18),
    'flyn': LED(22),
}
COMMANDS = ['on', 'off', 'pulse']

CSS = """
    .medium {
        font-size: 60px;
    }
    .larger {
        font-size: 80px;
    }
"""

def prog1(page_data={}):
    for u in CIRCUITS.keys():
        CIRCUITS[u].off()
        page_data[u] = 'OFF'

    CIRCUITS['posi'].blink(n=1, fade_in_time=1, fade_out_time=0, off_time=0, wait=True)
    CIRCUITS['posi'].on()
    #sleep(1)
    #CIRCUITS['head'].blink(n=1, on_time=0.1, off_time=0, fade_out_time=0.1, wait=True)
    sleep(2)
    CIRCUITS['time'].blink(n=1, on_time=0.1, off_time=0.1, wait=True)
    CIRCUITS['time'].blink(n=14, on_time=0.05, off_time=0.05, wait=True)
    CIRCUITS['time'].blink(n=5, on_time=0.1, off_time=0.1, wait=True)
    CIRCUITS['time'].blink(n=3, on_time=0.2, off_time=0.2, wait=True)
    CIRCUITS['time'].blink(n=1, fade_out_time=3, wait=True)
    sleep(2)
    CIRCUITS['posi'].off()

    return page_data


class WebServer(object):
    def __init__(self, ssid, pw):
        ip = self.connect(ssid, pw)
        self.conn = self.open_socket(ip)

    def connect(self, ssid, pw):
        #Connect to WLAN
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(ssid, pw)
        while wlan.isconnected() == False:
            print('Waiting for connection...')
            sleep(1)
        ip = wlan.ifconfig()[0]
        sleep(3)
        print(f'Connected on {ip}')
        #CIRCUITS['time'].pulse(2, 2, n=2)
        prog1()
        return ip

    def open_socket(self, ip):
        # Open a socket
        address = (ip, 80)
        connection = socket.socket()
        connection.bind(address)
        connection.listen(1)
        return connection

    def serve(self):
        #Start a web server
        page_data = {k: 'OFF' for k in CIRCUITS.keys()}
        page_data['css'] = CSS
        page_data['temperature'] = 0

        with open('index_template.html', 'r+') as f:
            html = f.read()

        while True:
            client = self.conn.accept()[0]
            request = client.recv(1024)
            request = str(request)
            try:
                request = request.split()[1]
            except IndexError:
                pass
            print(request)
            unit = request[1:5]
            command = request[5:-1]
            if unit in CIRCUITS.keys() and command in COMMANDS:
                if command == 'on':
                    CIRCUITS[unit].on()
                elif command == 'off':
                    CIRCUITS[unit].off()
                elif command == 'pulse':
                    CIRCUITS[unit].blink(on_time=0, off_time=1, fade_in_time=6, fade_out_time=3)
                page_data[unit] = command.upper()
            elif unit == 'prog':
                if command == '1':
                    page_data = prog1(page_data)

            page_data['temperature'] = pico_temp_sensor.temp

            client.send(html.format(**page_data))
            client.close()

CIRCUITS['posi'].blink(n=1)
ws = WebServer(CONFIG['SSID'], CONFIG['PASSWORD'])
ws.serve()
