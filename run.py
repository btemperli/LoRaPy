import json
from helium import Helium
from gps import get_gps_data
helium = Helium()
helium.transact("Test")
while True:
    gps_data = get_gps_data()
    response = {}
    if gps_data:
        response = helium.transact(json.dumps(gps_data))
    time.sleep(response.get("next_ping_at", 10))
