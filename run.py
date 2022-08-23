import time
import json
from helium import Helium
from gps import get_gps_data
get_gps_data()
def fire_ping():
    gps_data = get_gps_data()
    response = {}
    if gps_data:
        response = helium.transact(json.dumps(gps_data or {})) or {}
    return response

helium = Helium()
while True:
    try:
        response = fire_ping()
        print(response)
        time.sleep(response.get("next_ping_at", 10))
    except:
        print("oops")
        time.sleep(10)
