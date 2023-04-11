import time
import machine
import network
import ssd1351
import ujson as json
import urequests as requests

# Set up network connection
with open("network.json") as networkConfig:
    network = json.load(networkConfig)
    localNetwork = network.WLAN(network.STA_IF)
    localNetwork.active(True)
    localNetwork.connect(network["ssid"], network["password"])
    while not localNetwork.isconnected():
        pass

# Set up service connection
with open("service.json") as serviceConfig:
    service = json.load(serviceConfig)
    serviceUrlGet = service["get"]
    serviceUrlPost = service["post"]
    

# Set up local node
with open("config.json") as localConfig:
    config = json.load(localConfig)
    localID = config["local"]
    remote01ID = config["remote01"]
    remote02ID = config["remote02"]
    
    
# Set up the OLED screen
spi = machine.SPI(1, baudrate=8000000, polarity=0, phase=0)
oled = ssd1351.SSD1351(spi, dc=machine.Pin(8), cs=machine.Pin(9), rst=machine.Pin(10))

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
    response = requests.get(serviceUrlGet)
    data = response.json()

    # Extract the data for each Pico W
    localData = None
    remote01Data = None
    remote02Data = None
    for item in data:
        if item['id'] == localID:
            localData = item['data']
        elif item['id'] == remote01Data:
            remote01Data = item['data']
        elif item['id'] == remote02Data:
            remote02Data = item['data']

    # Display the data on the OLED screen
    oled.fill(ssd1351.color565(0, 0, 0))
    oled.text(localData['friendlyName'] + ':', 0, 0)
    oled.text(localData['status'], 0, 10, colors[localData['status']])
    oled.text(remote01Data['friendlyName'] + ':', 0, 20)
    oled.text(remote01Data['status'], 0, 30, colors[remote01Data['status']])
    oled.text(remote02Data['friendlyName'] + ':', 70, 0)
    oled.text(remote02Data['status'], 70, 10, colors[remote02Data['status']])
    oled.show()

    # Check if any of the remote Pico W's status is 'Summon'
    if remote01Data['status'] == 'Summon':
        summonActive = remote01ID
    elif remote02Data['status'] == 'Summon':
        summonActive = remote02ID
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
        if localData['status'] == 'Free' and summonActive is not None:
            # Buzz the piezo buzzer
            buzzer.on()
            time.sleep(0.5)
            buzzer.off()
            time.sleep(0.5)

    # Check if any button is pressed
    newStatus = ''
    if not button1.value():
        newStatus = 'Free'
    elif not button2.value():
        newStatus = 'In A Meeting'
    elif not button3.value():
        newStatus = 'Busy'
    elif not button4.value():
        newStatus = 'Summon'

    if newStatus != '':
        payload = {'status': newStatus}
        response = requests.post(serviceUrlPost + id, data=json.dumps(payload))

        # Check if the request was successful
        if response.status_code == 200:
            print('Record updated successfully')
        else:
            print('Error updating record')
            
    time.sleep(0.1)
