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
from machine import Pin, I2C
import ssd1306
import json
import time
import os

app = Microdot()

def init():
    global mode, display, f, line
#    os.dupterm(log_a)
#     for line in log_r:
#         l = l + line 
    
    
        
    display.text('Starting...', 0, 0, 1)
    try:
        file = open("config.json","r")
        config = json.loads(file.read())
        print('config = ', config)
        mode = config['mode']
    except:
        mode = 1
    else:
        file.close()
    set_mode(mode)
    display.fill(0)

async def init_network():
    global ip_addr, mode
    
    ssid = 'HIPPO'
    password = '8abcdef892'


    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.disconnect()
    ip_addr = wlan.ifconfig()[0]
    print('Подключено к Wi-Fi. IP-адрес:', ip_addr, ':5000')
    if not wlan.isconnected():
        wlan.connect(ssid, password)
        print("Waiting for connection...")
        display.fill_rect(0, 0, 128, 11, 0)
        display.text('Connecting...', 0, 0, 1)
        while not wlan.isconnected():
            await uasyncio.sleep(1)

    print("Connected... IP: " + ip_addr)
    display.fill_rect(0, 0, 128, 11, 0) 


Response.default_content_type = 'text/html'

temp = "1"

@app.get('/')
async def index(req):
    return Template('index.html').render(temp=sensor.temperature(), hum=humidity, mode=mode, on_off_motor=on_off_dict[motor.value()])


@app.get('/css')
async def css(req):
    return send_file('/static/css/styles.css')

@app.get('/js')
async def js(req):
    return send_file('/static/js/main.js')

@app.get('/qr-code')
async def qrCode(req):
    return send_file('/static/img/qr-code.png')

@app.get('/github-icon')
async def githubIcon(req):
    return send_file('/static/img/git-hub-img.svg')


    
# Методы (def)
@app.route("/heater_on")
def heater_on(request):
    heater.value(1)
    
# @app.route("/inf1")
# def inf1(request):
#     await request.write("HTTP/1.0 302 OK\r\n")
#     await request.write('Location: https://fermerznaet.com/pticevodstvo/perepela/inkubaciya.html#m5')
    
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
def fan_off(request):
    motor.value(1)

@app.route("/motor_off")
def fan_off(request):
    motor.value(0)

def set_mode(new_mode):
    global mode, target_temperature, target_humidity
    mode = new_mode
    if mode == 1:
    #С 1 по 7 день: температура - 37,8 C°, влажность - 50-55%.
        target_temperature = 37.8
        target_humidity = 53
    elif mode == 2:
        #С 8 по 14 день: температура - 37,8 C°, влажность - 45%.
        target_temperature = 37.8
        target_humidity = 45
    elif mode == 3:
        #С 15 по 17 день: температура - 37,5 C°, влажность - 65-70%.
        target_temperature = 37.5
        target_humidity = 67

def save_settings(mode):
    file = open("config.json","w")
    file.write(json.dumps({'mode': mode}))
    file.close()
    

async def tray_rotator():
    if mode == 1:
        while True:
            motor.value(1)
            await uasyncio.sleep(rotate_time) 
            motor.value(0)
            await uasyncio.sleep(2160) 
    elif mode == 2:
        while True:
            motor.value(1)
            await uasyncio.sleep(rotate_time) 
            motor.value(0)
            await uasyncio.sleep(14400)
    elif mode == 3:
        motor.value(0)
        
async def cooling():
    global cooling_mode 
    fan.value(1)
    cooling_mode = True
    await uasyncio.sleep(20)
    fan.value(0)
    cooling_mode = False
    if mode == 2:
        while True:
            await uasyncio.sleep(7200)
            fan.value(1)
            cooling_mode = True
            await uasyncio.sleep(900)
            fan.value(0)
            cooling_mode = False

async def demo():
    while True:
        heater.value(1)
        await uasyncio.sleep(60)
        heater.value(0)
        await uasyncio.sleep(30)

        motor.value(1)
        await uasyncio.sleep(30)
        motor.value(0)
        await uasyncio.sleep(30)

        fan.value(1)
        await uasyncio.sleep(30)
        fan.value(0)
        await uasyncio.sleep(30)

        global temperature, humidity, mode, ip_addr
        print("thermostat demo is running")
        try:
            sensor.measure()
            temperature = sensor.temperature()
            humidity = sensor.humidity()
            print(temperature, humidity)
        except:
                sensor.measure()
                temperature = sensor.temperature()
                humidity = sensor.humidity()
                print("Ошибка датчика")
        led.value(not led.value())
        on_off_dict = {1: "ON", 0: "OFF"}
        display.fill_rect(0, 12, 128, 64, 0) 
        display.text('Heat: {heat}, {temp}C'.format(heat = on_off_dict[heater.value()], temp = temperature), 0, 16, 1)
        display.text('Fan: {fan}, {hum}%'.format(fan = on_off_dict[fan.value()], hum = humidity), 0, 28, 1)
        display.text('M{mode}: {temp}C, {hum}%'.format(mode = mode, temp = target_temperature, hum = target_humidity) , 0, 40, 1)
        display.text(ip_addr, 0, 52, 1)

        display.show()        
        await uasyncio.sleep(2)     



async def thermostat():
    global temperature, humidity, mode, ip_addr
    print("thermostat is running")
    start_time = time.time()
    while True:
        if not cooling_mode:  
            try:
                sensor.measure()
                temperature = sensor.temperature()
                humidity = sensor.humidity()
                print(temperature, humidity)
            except:
                sensor.measure()
                temperature = sensor.temperature()
                humidity = sensor.humidity()
                print("Ошибка датчика")
            if temperature >= target_temperature:
                heater.value(0)
            elif temperature < target_temperature:
                heater.value(1)
            if humidity > target_humidity + delta_humidity:
                fan.value(1)
            elif humidity < target_humidity - delta_humidity:
                fan.value(0)
        
        led.value(not led.value())
        on_off_dict = {1: "ON", 0: "OFF"}
        display.fill_rect(0, 12, 128, 64, 0) 
        display.text('Heat: {heat}, {temp}C'.format(heat = on_off_dict[heater.value()], temp = temperature), 0, 16, 1)
        display.text('Fan: {fan}, {hum}%'.format(fan = on_off_dict[fan.value()], hum = humidity), 0, 28, 1)
        display.text('M{mode}: {temp}C, {hum}%'.format(mode = mode, temp = target_temperature, hum = target_humidity) , 0, 40, 1)
        display.text(ip_addr, 0, 52, 1)

        display.show()        
        await uasyncio.sleep(2)                



led = Pin(2, Pin.OUT)
sensor = dht.DHT22(Pin(25))
print(sensor.temperature())
heater = Pin(27, Pin.OUT)
fan = Pin(26, Pin.OUT)
motor = Pin(18, Pin.OUT)
display = ssd1306.SSD1306_I2C(128, 64, I2C(sda=Pin(23), scl=Pin(22)))

mode = 1
target_temperature = 37.8
target_humidity = 53
delta_temperature = .3
delta_humidity = 3
rotate_time = 10

seven_days1 = 10
forteen_days1 = 20
seven_days = 7*24*60*60
forteen_days = 14*24*60*60

humidity = 0
temperature = 0
ip_addr = ''
on_off_dict = {1: "ON", 0: "OFF"}


led.value(1)
#wait hardware init after hard reset
#sleep(5)

led.value(0)

init()


loop = uasyncio.get_event_loop()
loop.create_task(init_network())
loop.create_task(app.start_server())
loop.create_task(cooling())
# loop.create_task(thermostat())
loop.create_task(demo())
loop.create_task(tray_rotator())

try:
    loop.run_forever()
finally:
    
    log_r.close()



