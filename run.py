import time
import json
from helium import Helium
from gps import get_gps_data, get_dist
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

def fire_ping(last_gps):
    logging.info('Last GPS was '+str(last_gps))
    gps_data = get_gps_data()
    logging.info('Latest GPS is '+str(gps_date))
    response = {}
    if gps_data and not last_gps or (last_gps.get("lat") and last_gps.get("lon") and gps_data.get("lat") and gps_data.get("lon") and get_dist(gps_data["lat"], gps_data["lon"], last_gps["lat"], last_gps["lon"])) > 0.05:
        logging.info('Wont send ping')
        #response = helium.transact(json.dumps(gps_data or {})) or {}
        if gps_data["lat"] and gps_data["lon"]:
            logging.info('Beginning Ping')
            response = helium.transact(str(round(gps_data["lat"], 5))+","+str(round(gps_data["lon"], 5)))
            logging.info('Ping response was '+str(response))
    else:
        logging.info('Will send ping')
    return response, gps_data

helium = Helium()
last_gps = {}
while True:
    try:
        response, last_gps = fire_ping(last_gps)
        print(response)
        time.sleep(int(response or "10"))
        #time.sleep(response.get("next_ping_at", 10))
    except:
        print("oops")
        time.sleep(10)
