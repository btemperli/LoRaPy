import requests
from helium_authenticator import HeliumAuthenticator
from helium_transactor import keys, HeliumTransactor

class Helium:
    def authenticate(self):
        authentication = HeliumAuthenticator.authenticate()
        keys.write(dict(**self.keys, **authentication))
        return authentication
            
    def register_device(self):
        # if we have never seen the device, build some ... machinery and APIs etc to register this device.
        # response = requests.get("http://somewebsite.com/register_device.json"+some_authentication_information)
        return None
        
    def __init__(self):
        self.keys = keys.get_keys()
        if not self.keys.get("deveui"):
            self.register_device()
        if not self.keys.get("nwskey"):
            self.authenticate()
        helium_keys = passed_keys or keys.get_keys()
        self.ht = HeliumTransactor(verbose, helium_keys)
        
            