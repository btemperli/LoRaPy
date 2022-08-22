import time
import json
from helium import Helium
from gps import get_gps_data
helium = Helium()
def fire_ping():
    gps_data = get_gps_data()
    response = {}
    if gps_data:
        response = helium.transact(json.dumps(gps_data)) or {}
    return response

while True:
    response = fire_ping()
    time.sleep(response.get("next_ping_at", 10))
