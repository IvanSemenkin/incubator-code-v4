import network
from microdot import Microdot, send_file
from microdot.utemplate import Template
from microdot import Response
import time
import uasyncio
import network
from machine import Pin
import machine
from time import sleep
import dht
from machine import Pin, SoftI2C
import ssd1306
import json
import time
import os
import io
import sys

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
    global ip_addr, mode, ssid
    ssid = 'HIPPO'
    password = '8abcdef892'
    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.disconnect()
    
    if not wlan.isconnected():
        wlan.connect(ssid, password)
        log("Waiting for connection...")
        display.fill_rect(0, 0, 128, 11, 0)
        display.text('Connecting...', 0, 0, 1)
        while not wlan.isconnected():
            await uasyncio.sleep(3)
            
    ip_addr = wlan.ifconfig()[0]
    log('Подключено к Wi-Fi. Веб-интерфейс: http://' + ip_addr + ':5000')
    display.fill_rect(0, 0, 128, 11, 0)

### Route handling

@app.get('/')
async def index(req):
    return Template('index.html').render()

@app.get('/css')
async def css(req):
    response = send_file('/static/css/styles.css')
    response.headers['Cache-Control'] = 'public, max-age=14400'
    return response

@app.get('/js')
async def js(req):
    response = send_file('/static/js/main.js')
    response.headers['Cache-Control'] = 'public, max-age=14400'
    return response

@app.get('/qr-code')
async def qrCode(req):
    response = send_file('/static/img/qr-code.png')
    response.headers['Cache-Control'] = 'public, max-age=14400'
    return response

@app.get('/github-icon')
async def githubIcon(req):
    response = send_file('/static/img/git-hub-img.png')
    response.headers['Cache-Control'] = 'public, max-age=14400'
    return response

@app.get('/chick-icon')
async def chickIcon(req):
    response = send_file('/static/img/cyplenok-color.jpg')
    response.headers['Cache-Control'] = 'public, max-age=14400'
    return response

@app.get('/log')
async def log_view(req):
    global log_file
    log_file.flush()
    f = open('/log.txt')
    return "<pre>{}</pre> <a href='/'>← Назад</a>".format(f.read())

@app.route("/heater_on")
def heater_on(request):
    heater.value(1)

@app.get('/json_file')
def json_file(request):
    return {
            "temp": temperature,
            "hum": humidity,
            "mode": mode,
            "motor_stat": on_off_dict[motor.value()],
           }

@app.route("/heater_off")
def heater_off(request):
    heater.value(0)

@app.route("/fan_on")
def fan_on(request):
    fan.value(1)

@app.route("/fan_off")
def fan_off(request):
    fan.value(0)

@app.route("/mode_1")
def mode_1(request):
    set_mode(1)
    save_settings(mode)

@app.route("/mode_2")
def mode_2(request):
    set_mode(2)
    save_settings(mode)

@app.route("/mode_3")
def mode_3(request):
    set_mode(3)
    save_settings(mode)

@app.route("/motor_on")
def motor_on(request):
    motor.value(1)

@app.route("/motor_off")
def motor_off(request):
    motor.value(0)

### Route handling end

async def overheat():
    print("overheat run", temperature)
    while True:
        if temperature > 38.5:
            if overheat_start_time is None:
                overheat_start_time = time.time()
                log("начало перегрева")# Запоминаем время начала перегрева
            else:
                elapsed_time = time.time() - overheat_start_time
                print("Перегрев повторился!!!")
                if elapsed_time >= 300:
                    log("Внимание! Перегрев! Температура выше 38°C более 10 минут.")
                    overheat_start_time = None  # Сброс времени после вывода сообщения
                    await uasyncio.sleep(7200)
                    fan.value(1)
                    cooling_mode = True
                    await uasyncio.sleep(600)
                    fan.value(0)
                    cooling_mode = False
        else:
            overheat_start_time = None
            log("Перегрева нет")
        await uasyncio.sleep(2)

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
        await uasyncio.sleep(30)
        motor.value(0)
        await uasyncio.sleep(180)

async def cooling():
    global cooling_mode
    cooling_mode = False
    if mode == 2:
        while True:
            await uasyncio.sleep(7200)
            fan.value(1)
            cooling_mode = True
            await uasyncio.sleep(900)
            fan.value(0)
            cooling_mode = False

async def thermostat():
    global temperature, humidity, mode, ip_addr
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
            await uasyncio.sleep(2)
            display.pixel(0, 0, 0)
            try:
                display.show()
            except:
                log('display error')

led = Pin(2, Pin.OUT)
ssid = "HIPPO"
sensor = dht.DHT22(Pin(25))
heater = Pin(27, Pin.OUT)
fan = Pin(26, Pin.OUT)
motor = Pin(18, Pin.OUT)
display = ssd1306.SSD1306_I2C(128, 64, SoftI2C(sda=Pin(23), scl=Pin(22)))

mode = 1
target_temperature = 37.8
target_humidity = 53
delta_temperature = 0.3
delta_humidity = 3
rotate_time = 10

seven_days1 = 10
forteen_days1 = 20
seven_days = 7 * 24 * 60 * 60
forteen_days = 14 * 24 * 60 * 60

humidity = 0
temperature = 0
ip_addr = ''
on_off_dict = {1: "ON", 0: "OFF"}
image_cache = {}

log_file = open("log.txt", "w")

init()

loop = uasyncio.get_event_loop()
loop.create_task(init_network())
loop.create_task(app.start_server())
loop.create_task(cooling())
loop.create_task(thermostat())
loop.create_task(overheat())
loop.create_task(tray_rotator())

try:
    loop.run_forever()
finally:
    log_file.close()
    os.dupterm(None)
    app.shutdown()