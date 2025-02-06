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

app = Microdot()

temp = "23"

@app.get('/')
async def index(req):
    return Template('index.html').render(temp=temp)

@app.get('/settings')
async def settings(req):
    return Template('settings.html').render()

@app.get('/inf')
async def inf(req):
    return Template('inf.html').render()

@app.get('/css')
async def css(req):
    return send_file('/static/css/styles.css')

@app.get('/js')
async def css(req):
    return send_file('/static/js/main.js')


    
# Методы (def)
@app.route("/heater_on")
def heater_on(request):
    heater.value(1)
    await request.write("HTTP/1.0 302 OK\r\n")
    await request.write('Location: /settings\r\n')
    
@app.route("/inf1")
def inf1(request):
    await request.write("HTTP/1.0 302 OK\r\n")
    await request.write('Location: https://fermerznaet.com/pticevodstvo/perepela/inkubaciya.html#m5')
    
@app.route("/heater_off")
def heater_off(request):
    heater.czdsxxvalue(0)
    await request.write("HTTP/1.0 302 OK\r\n")
    await request.write('Location: /settings\r\n')
    
@app.route("/fan_on")
def fan_on(request):
    fan.value(1)
    await request.write("HTTP/1.0 302 OK\r\n")
    await request.write('Location: /settings\r\n')
    
@app.route("/fan_off")
def fan_off(request):
    fan.value(0)
    await request.write("HTTP/1.0 302 OK\r\n")
    await request.write('Location: /settings\r\n')
    
@app.route("/mode_1")    
def mode_1(request):
    set_mode(1)
    save_settings(mode)
    
    await request.write("HTTP/1.0 302 OK\r\n")
    await request.write('Location: /settings\r\n')    

@app.route("/mode_2")    
def mode_2(request):
    set_mode(2)
    save_settings(mode)
    await request.write("HTTP/1.0 302 OK\r\n")
    await request.write('Location: /settings\r\n')
    
@app.route("/mode_3")    
def mode_3(request):
    set_mode(3)
    save_settings(mode)
    await request.write("HTTP/1.0 302 OK\r\n")
    await request.write('Location: /settings\r\n')

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
    
async def thermostat():
    global temperature, humidity, mode, ip_addr
    start_time = time.time()
    while True:
        sensor.measure()
        temperature = sensor.temperature()
        humidity = sensor.humidity()
        if temperature >= target_temperature:
            heater.value(0)
        elif temperature < target_temperature:
            heater.value(1)
            
    
        #print(0 - (start_time - time.time()), "\t", temperature)
            
        if humidity > target_humidity + delta_humidity:
            fan.value(1)
        elif humidity < target_humidity - delta_humidity:
            fan.value(0)
# Перегрев
#         if temperature > 39:
#             fan.value(1)
#             display.text('Overheat fan ON!!!', 0, 0, 1)
#         elif temperature < 38.5:
#             fan.value(0)
#             display.fill_rect(0, 0, 128, 11, 0)
            
#         if temperature < 38:
#             display.text('Undercooling!!!', 0, 0, 1)
#         elif temperature > 37.2:
#             display.fill_rect(0, 0, 128, 11, 0)
        
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
sensor = dht.DHT22(Pin(14))
heater = Pin(13, Pin.OUT)
fan = Pin(12, Pin.OUT)
display = ssd1306.SSD1306_I2C(128, 64, I2C(sda=Pin(23), scl=Pin(22)))

mode = 1
target_temperature = 37.8
target_humidity = 53
delta_temperature = .3
delta_humidity = 3

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
loop.create_task(app.run())
loop.create_task(thermostat())
try:
    loop.run_forever()
finally:
    
    log_r.close()



