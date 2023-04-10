import time
import machine
import network
import ssd1306
import ujson
import urequests

# Set up network connection
with open("network.json") as networkConfig:
    network = ujson.load(networkConfig)
    localNetwork = network.WLAN(network.STA_IF)
    localNetwork.active(True)
    localNetwork.connect(network["ssid"], network["password"])
    while not localNetwork.isconnected():
        pass

# Set up service connection
with open("service.json") as serviceConfig:
    service = ujson.load(serviceConfig)
    serviceUrlGet = service["get"]
    serviceUrlPost = service["post"]
    

# Set up local node
with open("config.json") as localConfig:
    config = ujson.load(localConfig)
    localName = config["local"]
    remote01Name = config["remote01"]
    remote02Name = config["remote02"]
    
    
# Set up the OLED screen
i2c = machine.I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)
oled = ssd1306.SSD1306_I2C(128, 32, i2c)

# Set up the buttons
button1 = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_UP)
button2 = machine.Pin(3, machine.Pin.IN, machine.Pin.PULL_UP)
button3 = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)
button4 = machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_UP)

# Set up the piezo buzzer
buzzer = machine.Pin(6, machine.Pin.OUT)



# Define the colors for each status
colors = {'Free': 0x00FF00, 'In A Meeting': 0xFF0000, 'Busy': 0xFFA500, 'Summon': 0x00FFFF}

while True:
    # Query the datasource for data
    response = urequests.get(serviceUrlGet)
    data = response.json()

    # Extract the data for each Pico W
    localData = None
    remote01Data = None
    remote02Data = None
    for item in data:
        if item['board'] == localName:
            localData = item['data']
        elif item['board'] == remote01Name:
            remote01Data = item['data']
        elif item['board'] == remote02Name:
            remote02Data = item['data']

    # Display the data on the OLED screen
    oled.fill(0)
    oled.text(localName + ':', 0, 0)
    oled.text(localData, 0, 10, colors[localData])
    oled.text(remote01Name + ':', 0, 20)
    oled.text(remote01Data, 0, 30, colors[remote01Data])
    oled.text(remote02Name + ':', 70, 0)
    oled.text(remote02Data, 70, 10, colors[remote02Data])
    oled.show()

    # Check if any of the remote Pico W's status is 'Summon'
    if remote01Data == 'Summon':
        summonActive = remote01Name
    elif remote02Data == 'Summon':
        summonActive = remote02Name
    else:
        summonActive = None

    if summonActive is not None:
        # Blink the OLED screen 5 times one second apart
        for i in range(5):
            oled.fill(0)
            oled.show()
            time.sleep(0.5)
            oled.fill(1)
            oled.show()
            time.sleep(0.5)

        # Check if any of
        if localData == 'Free' and summonActive is not None:
            # Buzz the piezo buzzer
            buzzer.on()
            time.sleep(0.5)
            buzzer.off()
            time.sleep(0.5)

    # Check if any button is pressed
    if not button1.value():
        status = 'Free'
        board = 'localNode'
        urequests.post(serviceUrlPost, json={'board': board, 'data': status})
    elif not button2.value():
        status = 'In A Meeting'
        board = 'localNode'
        urequests.post(serviceUrlPost, json={'board': board, 'data': status})
    elif not button3.value():
        status = 'Busy'
        board = 'localNode'
        urequests.post(serviceUrlPost, json={'board': board, 'data': status})
    elif not button4.value():
        status = 'Summon'
        board = 'localNode'
        urequests.post(serviceUrlPost, json={'board': board, 'data': status})
        
    time.sleep(0.1)
