import sys
import time
import datetime

import adafruit_ssd1306
from SX127x.LoRa import LoRa, MODE
from digitalio import DigitalInOut, Direction, Pull
from SX127x.board_config_ada import BOARD
import board
import busio

from helium import Helium
# Button A
btnA = DigitalInOut(board.D5)
btnA.direction = Direction.INPUT
btnA.pull = Pull.UP

# Button B
btnB = DigitalInOut(board.D6)
btnB.direction = Direction.INPUT
btnB.pull = Pull.UP

# Button C
btnC = DigitalInOut(board.D12)
btnC.direction = Direction.INPUT
btnC.pull = Pull.UP

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)

# 128x32 OLED Display
reset_pin = DigitalInOut(board.D4)
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, reset=reset_pin)
# Clear the display.
width = display.width
height = display.height

def run():
    helium = Helium()
    running_ping = False
    last_test = datetime.datetime.fromtimestamp(0)
    ping_count = 0
    while True:
        time.sleep(.1)
        display.fill(0)
        display.text("Test is "+str(running_ping), 0, 0, 1)
        display.text('Time: '+str(helium.get_last_message()), 0, 10, 1)
        display.text('Total Pings: '+str(ping_count), 0, 20, 1)
        display.show()
        if running_ping and (datetime.datetime.now() - last_test).seconds > 5:
            helium.transact("Test")
            ping_count += 1
        if not btnA.value:
            running_ping = True
        if not btnB.value:
            running_ping = False
        if not btnC.value:
            display.fill(0)
            display.text("Test is shut down!", 0, 0, 1)
            display.text('Must restart PI to', 0, 10, 1)
            display.text('restart test.', 0, 20, 1)
            display.show()
            raise KeyboardInterrupt

run()