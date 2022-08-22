import os
import serial
import adafruit_gps
import time
uart = serial.Serial(os.popen("ls /dev/ttyUSB*").read().strip(), baudrate=9600, timeout=10)
gps = adafruit_gps.GPS(uart, debug=False)
gps.send_command(b'PMTK314,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0')
gps.send_command(b'PMTK220,2000')
last_print = time.monotonic()
def get_gps_data():
    gps.update()
    if gps.has_fix:
        return {"lat": gps.latitude, "lon": gps.longitude, "speed": gps.speed_knots, "alt": gps.altitude_m}
