# import
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

from nanoweb import Nanoweb

naw = Nanoweb()
#log_a = open('log.txt', 'a')



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
    
    wlan_id = "Ivans"
    wlan_pass = "parols01"

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.disconnect()
    if not wlan.isconnected():
        wlan.connect(wlan_id, wlan_pass)
        print("Waiting for connection...")
        display.fill_rect(0, 0, 128, 11, 0)
        display.text('Connecting...', 0, 0, 1)
        while not wlan.isconnected():
            await uasyncio.sleep(1)
            
    #wlan.disconnect()
    
    ip_addr = wlan.ifconfig()[0]
    print("Connected... IP: " + ip_addr)
    display.fill_rect(0, 0, 128, 11, 0) 

@naw.route("/")    
def index(request):
    global temperature, humidity, mode, line
    #with open('log.txt', 'r') as log_r:
     #   l = ''
      #  for line in log_r: 
       #     l = l + line
        #    l = l + '''</br>'''
    sensor.measure()
    temperature = sensor.temperature()
    humidity = sensor.humidity()
    
    html = '''
        <!DOCTYPE HTML>
        <html>
            <head>
              <meta charset="utf-8">
              <meta http-equiv="refresh" content="2">
              <title>Инкубатор</title>
            </head>
            <body style="height: 800px; font-size: 50px;">
                <a href="/">Главная</a>
                <a href="/settings">Настройки</a>
                <a href="/inf">Информация</a>
                <hr>
            <h1>Только для препелов!</h1>
                <hr>
            <h2><em>Показатели с DHT 22</em></h2>
            <ul>
                <li><b>Температура {temp} {heater_status}</b></li>
                <li><b>Влажность {hum} {fan_status}</b></li>
                <li><b>Сейчас режим: {mode}</b></li>  
            </ul>
            </body>
        </html>
        '''.format(temp = temperature,
               hum = humidity,
                fan_status = on_off_dict[fan.value()],
                heater_status = on_off_dict[heater.value()],
                mode = mode)
    await request.write("HTTP/1.0 200 OK\r\n")
    await request.write("Content-Type: text/html; charset=utf-8\r\n\r\n")
    await request.write(html)
    
@naw.route("/settings")       
def settings(request):
    on_off_dict = {1: "ON", 0: "OFF"}
    global mode
    
    
    html = '''
        <!DOCTYPE HTML>
    <html>
    <head>
      <meta charset="utf-8">
      <meta http-equiv="refresh" content="2">
      <title>Настройки (инкубатор)</title>
    </head>
    <body>
        <nav style="font-size: 50px;">
        <a href="/">Главная</a>
        <a href="/settings">Настройки</a>
        <a href="/inf">Информация</a>
        </nav>
        <hr>
        <h2><em>Подогрев {heater_status} {temp}</em></h2>
        <ul>
            <li><b><a href="/heater_on">Включить нагрев</a></b></li>      
            <li><b><a href="/heater_off">Выключить нагрев</a></b></li>
        </ul>
        <h2><em>Вентилятор {fan_status} {hum}</em></h2>
        <ul>
            <li><b><a href="/fan_on">Включить вентилятор</a></b></li>   
            <li><b><a href="/fan_off">Выключить вентилятор</a></b></li>
        </ul>
        <h2><em>Режимы инкубации</em></h2>
        <ul>
            <li><b><a href="/mode_1">Режим 1</a></b></li>
            <li><b>С 1 по 7 день: температура - 37,8 C°, влажность - 50-55%</b></li>
            <li><b><a href="/mode_2">Режим 2</a></b></li>
            <li><b>С 8 по 14 день: температура - 37,8 C°, влажность - 45%.</b></li>
            <li><b><a href="/mode_3">Режим 3</a></b></li>
            <li><b>С 15 по 17 день: температура - 37,5 C°, влажность - 65-70%</b></li>
            <li><b>Сейчас режим: {mode}</b></li>
        </ul>
     </body>
    </html>
    
     '''.format(
            temp = temperature,
            hum = humidity,fan_status = on_off_dict[fan.value()],
            heater_status = on_off_dict[heater.value()],
            mode = mode
        )
    await request.write("HTTP/1.0 200 OK\r\n")
    await request.write("Content-Type: text/html; charset=utf-8\r\n\r\n")
    await request.write(html)

    
@naw.route("/inf")       
def inf(request):
    
    html = '''
    <!DOCTYPE HTML>
    <html>
    <head>
      <meta charset="utf-8">
      <meta http-equiv="refresh" content="2">
      <title>Информация (инкубатор)</title>
    </head>
    <body>
        <a href="/">Главная</a>
        <a href="/settings">Настройки</a>
        <a href="/inf">Информация</a>
        <hr>
        <ul>
            <li>28.11.2022</li>
            <li>04.10.2024</li>
            <li>Подключение к сети обязательно!</li>
        </ul>
     </body>
    </html>
    '''
    
    

    await request.write("HTTP/1.0 200 OK\r\n")
    await request.write("Content-Type: text/html; charset=utf-8\r\n\r\n")
    await request.write(html)
    
    
# Методы (def)
@naw.route("/heater_on")
def heater_on(request):
    heater.value(1)
    await request.write("HTTP/1.0 302 OK\r\n")
    await request.write('Location: /settings\r\n')
    
@naw.route("/inf1")
def inf1(request):
    await request.write("HTTP/1.0 302 OK\r\n")
    await request.write('Location: https://fermerznaet.com/pticevodstvo/perepela/inkubaciya.html#m5')
    
@naw.route("/heater_off")
def heater_off(request):
    heater.czdsxxvalue(0)
    await request.write("HTTP/1.0 302 OK\r\n")
    await request.write('Location: /settings\r\n')
    
@naw.route("/fan_on")
def fan_on(request):
    fan.value(1)
    await request.write("HTTP/1.0 302 OK\r\n")
    await request.write('Location: /settings\r\n')
    
@naw.route("/fan_off")
def fan_off(request):
    fan.value(0)
    await request.write("HTTP/1.0 302 OK\r\n")
    await request.write('Location: /settings\r\n')
    
@naw.route("/mode_1")    
def mode_1(request):
    set_mode(1)
    save_settings(mode)
    
    await request.write("HTTP/1.0 302 OK\r\n")
    await request.write('Location: /settings\r\n')    

@naw.route("/mode_2")    
def mode_2(request):
    set_mode(2)
    save_settings(mode)
    await request.write("HTTP/1.0 302 OK\r\n")
    await request.write('Location: /settings\r\n')
    
@naw.route("/mode_3")    
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
display = ssd1306.SSD1306_I2C(128, 64, I2C(sda=Pin(0), scl=Pin(2)))

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
loop.create_task(naw.run())
loop.create_task(thermostat())
try:
    loop.run_forever()
finally:
    
    log_r.close()