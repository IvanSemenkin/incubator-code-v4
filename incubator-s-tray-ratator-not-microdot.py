# import
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
    global ip_addr, mode, wlan
    
    wlan_id = "HIPPOPOX"
    wlan_pass = "8abcdef892"

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
        <!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta http-equiv="refresh" content="2" />
    <title>Инкубатор</title>
    <link rel="stylesheet" href="/styles.css"/>
  </head>
  <body>
    <nav>
        <a href="/">Главная</a>
        <a href="/settings">Настройки</a>
        <a href="/inf">Информация</a>
    </nav>

    <div class="main-div">
      <h1>Только для препелов!</h1>
      <h2><em>Показатели с DHT 22</em></h2>
      <ul>
        <li><b>Температура {temp} {heater_status}</b></li>
        <li><b>Влажность {hum} {fan_status}</b></li>
        <li><b>Сейчас режим: {mode}</b></li>
      </ul>
    </div>
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
      <link rel="stylesheet" href="/styles.css"/>
    </head>
    <body>
        <nav>
            <a href="/">Главная</a>
            <a href="/settings">Настройки</a>
            <a href="/inf">Информация</a>
        </nav>
        <div class="main-div">
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
        </div>
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
            <li>28.11.2022.18.9</li>
            <li>04.10.2024.18.9</li>
            <li>Подключение к сети обязательно!</li>
        </ul>
     </body>
    </html>
    '''
    
    

    await request.write("HTTP/1.0 200 OK\r\n")
    await request.write("Content-Type: text/html; charset=utf-8\r\n\r\n")
    await request.write(html)
    
    
@naw.route("/styles.css")
async def serve_styles(request):
    try:
        # Open the CSS file from the filesystem
        with open("/styles.css", "r") as file:
            css_content = file.read()
        
        # Send the CSS content with the correct content type
        await request.write("HTTP/1.0 200 OK\r\n")
        await request.write("Content-Type: text/css; charset=utf-8\r\n\r\n")
        await request.write(css_content)
    except Exception as e:
        # If the file cannot be found or there's an error, return a 404
        print(f"Error: {e}")
        await request.write("HTTP/1.0 404 Not Found\r\n")
        await request.write("Content-Type: text/plain\r\n\r\n")
        await request.write("File not found")

    
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
    file.write(json.dumps({'start_time_onl': start_time_onl}))
    file.close()
    
    
async def tray_rotator():
    while True:
        if mode == 1:
            motor.value(1)
            await uasyncio.sleep(rotate_time) 
            motor.value(0)
            await uasyncio.sleep(2160) 
        elif mode == 2:
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
    while True:
        if mode == 2:
            await uasyncio.sleep(7200)
            fan.value(1)
            cooling_mode = True
            await uasyncio.sleep(900)
            fan.value(0)
            cooling_mode = False
            await uasyncio.sleep(43200)

# async def automatic_mode_change():
#     global start_time_onl
#     await uasyncio.sleep(5)
#     isconnected = wlan.isconnected()
#     start_time_onl = time.time()
#     
# #     print(start_time)
# #     await uasyncio.sleep(2)
# #     print(start_time - time.time())
#     while True:
#         if isconnected:
#             passed_time = time.time() - start_time_onl
#             if passed_time <= seven_days1 and passed_time >= 0:
#                 print('mode set 1')
#                 mode = 1
#                 save_settings(mode)
#             elif passed_time >= seven_days1 and passed_time < forteen_days1:
#                 print('mode set 2')
#                 mode = 2
#                 save_settings(mode)
#             elif passed_time >= forteen_days1:
#                 print('mode set 3')
#                 mode = 3
#                 save_settings(mode)
#         await uasyncio.sleep(2)
#         
#         
#     else:
#         #нету подключения к интернету
#         mode = 1
#         save_settings(mode)
#         print('mode set 1')
#         await uasyncio.sleep(seven_days_1)
#         mode = 2
#         save_settings(mode)
#         print('mode set 2')
#         await uasyncio.sleep(forteen_days1)
#         mode = 3
#         print('mode set 3')
#         save_settings(mode)
        
    
async def thermostat():
    global temperature, humidity, mode, ip_addr, cooling_mode
    start_time = time.time()
    while True:
        try:
            sensor.measure()
        except OSError as e:
            print('Failed to read sensor.')
        temperature = sensor.temperature()
        humidity = sensor.humidity()
        if temperature >= target_temperature:
            heater.value(0)
        elif temperature < target_temperature:
            heater.value(1)
            
    
        print(0 - (start_time - time.time()), "\t", temperature)
        if not cooling_mode:
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


cooling_mode = False
led = Pin(2, Pin.OUT)
dht_pin = machine.Pin(4)
sensor = dht.DHT22(Pin(25))
heater = Pin(27, Pin.OUT)
fan = Pin(26, Pin.OUT)
motor = Pin(18, Pin.OUT)
display = ssd1306.SSD1306_I2C(128, 64, SoftI2C(sda=Pin(23), scl=Pin(22)))

mode = 1
target_temperature = 37.8
target_humidity = 53
delta_temperature = .3
delta_humidity = 3
rotate_time = 5

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
loop.create_task(naw.run())
loop.create_task(thermostat())
loop.create_task(tray_rotator())
loop.create_task(cooling())
# loop.create_task(automatic_mode_change())

try:
    loop.run_forever()
finally:
    log_a.close()
    log_r.close()
    \