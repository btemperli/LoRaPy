import time
import json
from helium import Helium
from gps import get_gps_data
def fire_ping():
    gps_data = get_gps_data()
    response = {}
    if gps_data:
        #response = helium.transact(json.dumps(gps_data or {})) or {}
        if gps_data["lat"] and gps_data["lon"]:
            response = helium.transact(str(round(gps_data["lat"], 5))+","+str(round(gps_data["lon"], 5)))
    return response

helium = Helium()
while True:
    try:
        response = fire_ping()
        print(response)
        time.sleep(int(response or "10"))
        #time.sleep(response.get("next_ping_at", 10))
    except:
        print("oops")
        time.sleep(10)
