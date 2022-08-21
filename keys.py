import dotenv
import json
import os

# puts the keys from .env file into the environment,
# so this can be configured from a file or env vars.
dotenv.load_dotenv()

# Get these values from console.helium.com under Device Details.
key_path = os.environ.get('key_path', 'keys.json')
if os.path.exists(key_path):
    filekeys = json.loads(open(key_path).read())
else:
    filekeys = {}

deveui = bytes.fromhex(os.environ.get('deveui', filekeys.get('deveui', '')))
appeui = bytes.fromhex(os.environ.get('appeui', filekeys.get('appeui', '')))
appkey = bytes.fromhex(os.environ.get('appkey', filekeys.get('appkey', '')))

# Fill in these values when you activate the device with otaa_helium.py. 
devaddr = json.loads(os.environ.get('devaddr', filekeys.get('devaddr', '[]')))
nwskey = json.loads(os.environ.get('nwskey', filekeys.get('nwskey', '[]')))
appskey = json.loads(os.environ.get('appskey', filekeys.get('appskey', '[]')))

def get_keys():
    return {
        "deveui": deveui,
        "appeui": appeui,
        "appkey": appkey,
        "devaddr": devaddr,
        "nwskey": nwskey,
        "appskey": appskey,
    
    }

def write(keys, path=key_path):
    f = open(path, 'w')
    f.write(json.dumps(keys))
    f.close()
    