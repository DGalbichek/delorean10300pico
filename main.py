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

def webpage(temperature, state):
    #Template HTML
    html = f"""
        <!DOCTYPE html>
        <html>
            <body>
                <form action="./posion">
                    <input type="submit" value="Posi on" />
                </form>
                <form action="./posioff">
                    <input type="submit" value="Posi off" />
                </form>
                <p>POSI is {state['posi']}</p>
                <form action="./headon">
                    <input type="submit" value="Head on" />
                </form>
                <form action="./headoff">
                    <input type="submit" value="Head off" />
                </form>
                <p>HEAD is {state['head']}</p>
                <form action="./timeon">
                    <input type="submit" value="Time on" />
                </form>
                <form action="./timeoff">
                    <input type="submit" value="Time off" />
                </form>
                <p>TIME is {state['time']}</p>
                <form action="./flynon">
                    <input type="submit" value="Flyn on" />
                </form>
                <form action="./flynoff">
                    <input type="submit" value="Flyn off" />
                </form>
                <p>FLYN is {state['flyn']}</p>
                <p>Temperature is {temperature}</p>
            </body>
        </html>
        """
    return str(html)

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
        state = {k: 'OFF' for k in CIRCUITS.keys()}
        temperature = 0
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
                state['head'] = 'ON'
            elif request =='/headoff?':
                CIRCUITS['head'].off()
                state['head'] = 'OFF'
            elif request == '/posion?':
                CIRCUITS['posi'].on()
                state['posi'] = 'ON'
            elif request =='/posioff?':
                CIRCUITS['posi'].off()
                state['posi'] = 'OFF'
            elif request == '/timeon?':
                CIRCUITS['time'].on()
                state['time'] = 'ON'
            elif request =='/timeoff?':
                CIRCUITS['time'].off()
                state['time'] = 'OFF'
            elif request == '/flynon?':
                CIRCUITS['flyn'].on()
                state['flyn'] = 'ON'
            elif request =='/flynoff?':
                CIRCUITS['flyn'].off()
                state['flyn'] = 'OFF'
            temperature = pico_temp_sensor.temp
            html = webpage(temperature, state)
            client.send(html)
            client.close()

CIRCUITS['posi'].blink(n=1)
ws = WebServer(CONFIG['SSID'], CONFIG['PASSWORD'])
ws.serve()
