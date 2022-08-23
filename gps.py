from gpsdclient import GPSDClient

client = GPSDClient(host="127.0.0.1")
def get_gps_data():
    for result in client.dict_stream(convert_datetime=True):
        if result["class"] == "TPV":
            return {"lat": result.get("lat"), "lon": result.get("lon"), "speed": result.get("speed"), "alt": result.get("alt")}
