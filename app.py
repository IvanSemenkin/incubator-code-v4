import uasyncio as asyncio

import network
import time
from time import sleep

import machine
from machine import Pin, SoftI2C
from machine import Pin

import os
import io
import sys
import json

from microdot import Microdot, send_file
from microdot.utemplate import Template
from microdot import Response

import dht
import ssd1306


app = Microdot()

def init():
    os.dupterm(log_file)
    display.rotate(False)
    display.text('Starting...', 0, 0, 1)
    
    try:
        file = open("config.json", "r")
        config = json.loads(file.read())
        log('config = ' + config)
        mode = config['mode']
    except:
        mode = 1
    else:
        file.close()
    
    set_mode(mode)
    
    display.fill(0)
    Response.default_content_type = 'text/html'


async def init_network():
    global ip_addr
    ssid = 'HIPPO'
    password = '8abcdef892'
    wlan = network.WLAN(network.WLAN.IF_STA)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            await asyncio.sleep(1)
    ip_addr = wlan.ifconfig()[0]
    log('Подключено к Wi-Fi. Веб-интерфейс: http://' + ip_addr + ':5000')
    display.fill_rect(0, 0, 128, 11, 0)
    
### Route handling

@app.get('/')
async def index(request):
    return Template('index.html').render()

@app.get('/settings')
async def index(request):
    return Template('settings.html').render()

@app.get('/static/<path:path>')
async def get_static(request, path):
    response = send_file('/static/' + path)
    response.headers['Cache-Control'] = 'public, max-age=14400'
    return response

@app.get('/api/data')
def get_data(request):
    return {
            "temp": temperature,
            "hum": humidity,
            "mode": mode,
            "motor_stat": on_off_dict[motor.value()],
            "heater_stat": on_off_dict[heater.value()],
            "fan_stat": on_off_dict[fan.value()],
           }

@app.get('/log')
async def log_view(req):
    global log_file
    log_file.flush()
    f = open('/log.txt')
    return "<pre>{}</pre> <a href='/'>← Назад</a>".format(f.read())


@app.get('/fan/<int:id>')
async def change_fan(request, id):
    fan.value(id)

@app.get('/mode/<int:id>')
async def change_mode(request, id):
    set_mode(id)
    save_settings(mode)

@app.get('/heater/<int:id>')
async def change_heater(request, id):
    heater.value(id)

@app.get('/motor/<int:id>')
async def change_motor(request, id):
    motor.value(id)


# @app.route("/motor_on")
# def motor_on(request):
#     motor.value(1)
# 
# @app.route("/motor_off")
# def motor_off(request):
#     motor.value(0)
    
### Route handling end
def set_mode(new_mode):
    global mode, target_temperature, target_humidity
    mode = new_mode
    if mode == 1:
        # С 1 по 7 день: температура - 37,8 C°, влажность - 50-55%.
        target_temperature = 37.8
        target_humidity = 53
    elif mode == 2:
        # С 8 по 14 день: температура - 37,8 C°, влажность - 45%.
        target_temperature = 37.8
        target_humidity = 45
    elif mode == 3:
        # С 15 по 17 день: температура - 37,5 C°, влажность - 65-70%.
        target_temperature = 37.5
        target_humidity = 67

def save_settings(mode):
    file = open("config.json", "w")
    file.write(json.dumps({'mode': mode}))
    file.close()

def log(msg):
    global log_file
    now = time.localtime()
    print("[{}-{}-{} {}:{}:{}] {}".format(now[2], now[1], now[0], now[3], now[4], now[5], msg))

async def tray_rotator():
    while True:
        motor.value(1)
        await asyncio.sleep(10)
        motor.value(0)
        await asyncio.sleep(3600)

async def thermostat():
    global temperature, humidity
    log("thermostat is running")
    start_time = time.time()
    while True:
        if not cooling_mode:
            try:
                sensor.measure()
                temperature = sensor.temperature()
                humidity = sensor.humidity()
            except:
                sensor.measure()
                temperature = sensor.temperature()
                humidity = sensor.humidity()
                log("Ошибка датчика")
                
            if temperature >= target_temperature:
                heater.value(0)
            elif temperature < target_temperature:
                heater.value(1)
                
            if humidity > target_humidity + delta_humidity:
                fan.value(1)
            elif humidity < target_humidity - delta_humidity:
                fan.value(0)
                
            log('temp: ' + str(temperature))
            led.value(not led.value())
            on_off_dict = {1: "ON", 0: "OFF"}
            display.fill_rect(0, 12, 128, 64, 0)
            display.text('Heat: {heat}, {temp}C'.format(heat=on_off_dict[heater.value()], temp=temperature), 0, 16, 1)
            display.text('Fan: {fan}, {hum}%'.format(fan=on_off_dict[fan.value()], hum=humidity), 0, 28, 1)
            display.text('M{mode}: {temp}C, {hum}%'.format(mode=mode, temp=target_temperature, hum=target_humidity), 0, 40, 1)
            display.text(ip_addr, 0, 52, 1)
            display.pixel(0, 0, 1)
            try:
                display.show()
            except:
                log('display error')
            await asyncio.sleep(2)
            display.pixel(0, 0, 0)
            try:
                display.show()
            except:
                log('display error')
                
                
mode = 1

led = Pin(2, Pin.OUT)
ssid = "HIPPO"
sensor = dht.DHT22(Pin(25))
heater = Pin(27, Pin.OUT)
fan = Pin(26, Pin.OUT)
motor = Pin(18, Pin.OUT)
display = ssd1306.SSD1306_I2C(128, 64, SoftI2C(sda=Pin(23), scl=Pin(22)))

cooling_mode = False
prev_temperature = None
prev_humidity = None
log_file_path = "log.json"
target_temperature = 37.8
target_humidity = 53
delta_temperature = 0.3
delta_humidity = 3
rotate_time = 10

seven_days1 = 10
forteen_days1 = 20
seven_days = 7 * 24 * 60 * 60
forteen_days = 14 * 24 * 60 * 60
overheat_mode = False
humidity = 0
temperature = 0
ip_addr = ''
on_off_dict = {1: "ON", 0: "OFF"}

log_file = open("log.txt", "w")

init()

loop = asyncio.get_event_loop()
loop.create_task(init_network())
loop.create_task(app.start_server())
loop.create_task(thermostat())
loop.create_task(tray_rotator())

try:
    loop.run_forever()
finally:
    log_file.close()
    os.dupterm(None)
    app.shutdown()