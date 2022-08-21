import requests
from helium_authenticator import HeliumAuthenticator
from helium_transactor import keys, HeliumTransactor

class Helium:
    def authenticate(self):
        authentication = HeliumAuthenticator.authenticate()
        cur_keys = self.keys
        for k,v in authentication.items():
            cur_keys[k] = v
        keys.write(cur_keys)
        return authentication
            
    def register_device(self):
        # if we have never seen the device, build some ... machinery and APIs etc to register this device.
        # response = requests.get("http://somewebsite.com/register_device.json"+some_authentication_information)
        return None

    def get_last_message(self):
        return self.ht.last_message

    def transact(self, msg):
        return self.ht.transact(msg)

    def __init__(self, passed_keys=None, verbose=False):
        self.keys = keys.get_keys()
        if not self.keys.get("deveui"):
            self.register_device()
        if not self.keys.get("nwskey"):
            self.authenticate()
        helium_keys = passed_keys or keys.get_keys()
        self.ht = HeliumTransactor.init(verbose, helium_keys)
        
            