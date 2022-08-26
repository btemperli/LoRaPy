import datetime
import time
import json
from helium import Helium
from gps import get_gps_data, get_dist, should_send_gps
import logging
import sys

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', 
                              '%m-%d-%Y %H:%M:%S')
file_handler = logging.FileHandler('/home/pi/run.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception

def fire_ping(last_gps, last_sent_at):
    logging.info('Last GPS was '+str(last_gps))
    gps_data = get_gps_data()
    logging.info('Latest GPS is '+str(gps_data))
    response = {}
    if should_send_gps(gps_data, last_gps, last_sent_at):
        logging.info('Will send ping')
        response = helium.transact(str(round(gps_data["lat"], 5))+","+str(round(gps_data["lon"], 5))+","+str(int(gps_data["speed"] or 0)))
        last_sent_at = datetime.datetime.now()
        logging.info('Ping response was '+str(response))
    else:
        logging.info('Wont send ping')
    return response, gps_data, last_sent_at

helium = Helium()
last_gps = {}
last_sent_at = None
while True:
    try:
        response, last_gps, last_sent_at = fire_ping(last_gps, last_sent_at)
        print(response)
        time.sleep(int(response or "10"))
        #time.sleep(response.get("next_ping_at", 10))
    except:
        print("oops")
        time.sleep(10)
