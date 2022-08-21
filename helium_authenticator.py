#!/usr/bin/env python3

import sys
from time import sleep
from SX127x.LoRa import *
from SX127x.LoRaArgumentParser import LoRaArgumentParser
from SX127x.board_config_ada import BOARD
import LoRaWAN
from LoRaWAN.MHDR import MHDR
from random import randrange
import reset_ada
import helium_helper
import keys

class HeliumAuthenticator(LoRa):
    def __init__(self, verbose=False, keys=keys.get_keys()):
        super(HeliumAuthenticator, self).__init__(verbose)
        self.authenticated = False
        self.devaddr = None
        self.nwskey = None
        self.appskey = None
        self.devnonce = [randrange(256), randrange(256)]
        self.keys = keys

    def on_rx_done(self):
        print("RxDone")

        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        print(payload)
        self.set_mode(MODE.SLEEP)
        self.get_all_registers()
        print(self)
        lorawan = LoRaWAN.new([], self.keys["appkey"])
        lorawan.read(payload)
        print(lorawan.get_payload())
        print(lorawan.get_mhdr().get_mversion())

        if lorawan.get_mhdr().get_mtype() == MHDR.JOIN_ACCEPT:
            self.devaddr = lorawan.get_devaddr()
            self.nwskey = lorawan.derive_nwskey(self.devnonce)
            self.appskey = lorawan.derive_appskey(self.devnonce)
            self.authenticated = True
        print("Got LoRaWAN message continue listen for join accept")

    def on_tx_done(self):
        self.clear_irq_flags(TxDone=1)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0,0,0,0,0,0])
        self.set_invert_iq(1)
        self.reset_ptr_rx()
        self.set_freq(helium_helper.DOWNFREQ)#915)        
        self.set_spreading_factor(7)#12)
        self.set_bw(9) #500Khz
        self.set_rx_crc(False)#TRUE
        self.set_mode(MODE.RXCONT)

    def setup_tx(self):
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([1,0,0,0,0,0])
        self.set_freq(helium_helper.UPFREQ)
        self.set_pa_config(pa_select=1)
        self.set_spreading_factor(7)
        self.set_pa_config(max_power=0x0F, output_power=0x0E)
        self.set_sync_word(0x34)
        self.set_rx_crc(True)
        self.get_all_registers()
        assert(self.get_agc_auto_on() == 1)

    def start(self):
        self.setup_tx()
        lorawan = LoRaWAN.new(self.keys["appkey"])
        lorawan.create(MHDR.JOIN_REQUEST, {'deveui': self.keys["deveui"], 'appeui': self.keys["appeui"], 'devnonce': self.devnonce})
        self.write_payload(lorawan.to_raw())
        self.set_mode(MODE.TX)
        sleep(10)

    @classmethod
    def authenticate(cls):
        BOARD.setup()
        lora = cls(True)
        try:
            print("Sending LoRaWAN join request\n")
            lora.start()
            lora.set_mode(MODE.SLEEP)
            print(lora)
        except KeyboardInterrupt:
            sys.stdout.flush()
            print("\nKeyboardInterrupt")
        finally:
            sys.stdout.flush()
            lora.set_mode(MODE.SLEEP)
            BOARD.teardown()
        return {"devaddr": lora.devaddr, "nwskey": lora.nwskey, "appskey": lora.appskey}
    