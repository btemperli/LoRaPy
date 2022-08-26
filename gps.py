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
    print(a)
    if not a:
        return 0
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance

def should_send_gps(new, old, last_sent_at):
    if last_sent_at is None:
        return True
    if not new:
        return False
    if new and not old:
        return True
    if new.get("lat") is not None and  new.get("lon") is not None and None in [old.get("lat"), old.get("lon")]:
        return True
    if None not in [new["lat"], new["lon"], old["lat"], old["lon"]]:
        distance = get_dist(new["lat"], new["lon"], old["lat"], old["lon"])
        if distance < 0.05:
            if (datetime.datetime.now() - last_sent_at).seconds > 60*5:
                return True
            else:
                return False
        else:
            return True
    else:
        return False
