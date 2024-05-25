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
        CIRCUITS['time'].pulse(2, 2, n=2)
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
        page_data['temperature'] = 0
        while True:
            client = self.conn.accept()[0]
            request = client.recv(1024)
            request = str(request)
            try:
                request = request.split()[1]
            except IndexError:
                pass
            print(request)
            if request == '/headon?':
                CIRCUITS['head'].on()
                page_data['head'] = 'ON'
            elif request =='/headoff?':
                CIRCUITS['head'].off()
                page_data['head'] = 'OFF'
            elif request == '/posion?':
                CIRCUITS['posi'].on()
                page_data['posi'] = 'ON'
            elif request =='/posioff?':
                CIRCUITS['posi'].off()
                page_data['posi'] = 'OFF'
            elif request == '/timeon?':
                CIRCUITS['time'].on()
                page_data['time'] = 'ON'
            elif request =='/timeoff?':
                CIRCUITS['time'].off()
                page_data['time'] = 'OFF'
            elif request == '/flynon?':
                CIRCUITS['flyn'].on()
                page_data['flyn'] = 'ON'
            elif request =='/flynoff?':
                CIRCUITS['flyn'].off()
                page_data['flyn'] = 'OFF'
            page_data['temperature'] = pico_temp_sensor.temp

            with open('index_template.html', 'r+') as f:
                html = f.read()
            client.send(html.format(**page_data))
            client.close()

CIRCUITS['posi'].blink(n=1)
ws = WebServer(CONFIG['SSID'], CONFIG['PASSWORD'])
ws.serve()
