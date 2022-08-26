from math import sin, cos, sqrt, atan2, radians
import datetime
from gpsdclient import GPSDClient

client = GPSDClient(host="127.0.0.1")
def get_gps_data(transact_timeout=10):
    start = datetime.datetime.now()
    for result in client.dict_stream(convert_datetime=True):
        (datetime.datetime.now() - start).seconds < transact_timeout
        if result["class"] == "TPV":
            return {"lat": result.get("lat"), "lon": result.get("lon"), "speed": result.get("speed"), "alt": result.get("alt")}


def get_dist(lat1,lon1,lat2,lon2):
    # approximate radius of earth in km
    R = 6373.0
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance or 10000