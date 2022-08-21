import sys
import time

import adafruit_ssd1306
from SX127x.LoRa import LoRa, MODE
from digitalio import DigitalInOut, Direction, Pull
from SX127x.board_config_ada import BOARD
import board
import busio

from helium_lora import HeliumLoRa

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
lora = HeliumLoRa.init(True, True, True)
try:
    print("Sending LoRaWAN join request\n")
    lora.start()
    lora.set_mode(MODE.SLEEP)
    print(lora)
except KeyboardInterrupt:
    sys.stdout.flush()
    print("\nKeyboardInterrupt")
finally:
    sys.stdout.flush()
    lora.set_mode(MODE.SLEEP)
    BOARD.teardown()
# def run():
#     lora = HeliumLoRa.init()
#     if not keys.nwskey:
#         devaddr, nwskey, appskey = lora.otaa()
#     while True:
#         time.sleep(.1)
#         display.fill(0)
#         display.text("Test is "+str(lora.test_status["running_ping"]), 0, 0, 1)
#         display.text('Time: '+str(lora.test_status["last_message"]), 0, 10, 1)
#         display.text('Total Pings: '+str(lora.test_status["ping_count"]), 0, 20, 1)
#         display.show()
#         if lora.test_status["running_ping"] and (datetime.datetime.now() - lora.last_test).seconds > 5:
#             lora.transact("Test")
#         if not btnA.value:
#             lora.test_status["running_ping"] = True
#         if not btnB.value:
#             lora.test_status["running_ping"] = False
#         if not btnC.value:
#             display.fill(0)
#             display.text("Test is shut down!", 0, 0, 1)
#             display.text('Must restart PI to', 0, 10, 1)
#             display.text('restart test.', 0, 20, 1)
#             display.show()
#             raise KeyboardInterrupt
#
# run()