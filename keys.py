import dotenv
import json
import os

# puts the keys from .env file into the environment,
# so this can be configured from a file or env vars.
dotenv.load_dotenv()

# Get these values from console.helium.com under Device Details.
deveui = bytes.fromhex(os.environ.get('deveui'))
appeui = bytes.fromhex(os.environ.get('appeui'))
appkey = bytes.fromhex(os.environ.get('appkey'))

# Fill in these values when you activate the device with otaa_helium.py. 
devaddr = json.loads(os.environ.get('devaddr', '[]'))
nwskey = json.loads(os.environ.get('nwskey', '[]'))
appskey = json.loads(os.environ.get('appskey', '[]'))
