# On Air   

> This is a work-in-progress. 

Allow a family to easily share their availability status across 2-3 Pico W's so there are no unwanted interruptions during remote work / video conferences.

---

## Prerequisites

### Hardware
- Pico W
- [Adafruit OLED Display](https://www.adafruit.com/product/1431)

### Install the required libraries
We will need the following libraries to interact with the OLED screen and connect to the datasource:
* Adafruit's SSD1351 OLED display library
* MicroPython's urequests library

To install these libraries, connect your Raspberry Pi Pico W to your computer and run the following commands in the REPL prompt:

```
import upip
upip.install('micropython-urequests')
upip.install("micropython-adafruit-ssd1351")
```

### Connect the OLED screen to your Raspberry Pi Pico W
Connect your OLED screen to your Raspberry Pi Pico W using the I2C protocol. Make sure the OLED screen is properly connected to the Pico W's pins.