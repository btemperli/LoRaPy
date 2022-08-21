#!/usr/bin/env python3

import os
import re
import json
import datetime
from time import sleep
from random import randrange

from SX127x.LoRa import LoRa, MODE
from SX127x.board_config_ada import BOARD
import LoRaWAN
from LoRaWAN.MHDR import MHDR
import shortuuid

import helium_helper
import keys
class HeliumTransactor(LoRa):
    def __init__(self, verbose=False, keys=keys.get_keys()):
        super(HeliumTransactor, self).__init__(verbose)
        self.iter = 0
        self.uuid = shortuuid.uuid()
        self.ack = True
        self.test_status = {"ping_count": 0, "last_message": None}
        self.last_tx = datetime.datetime.fromtimestamp(0)
        self.last_message = None
        self.transact_timeout = 5
        self.keys = keys

    def on_rx_done(self):
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        print("Raw payload: {}".format(payload))
        lorawan = LoRaWAN.new(self.keys["nwskey"], self.keys["appskey"])
        lorawan.read(payload)
        decoded = "".join(list(map(chr, lorawan.get_payload())))
        print(decoded)
        import code;code.interact(local=dict(globals(), **locals())) 
        self.last_message = decoded
        self.test_status["last_message"] = decoded
        self.test_status["ping_count"] += 1
        print("Decoded: {}".format(decoded))
        print("\n")
        if lorawan.get_mhdr().get_mtype() == MHDR.UNCONF_DATA_DOWN:
            print("Unconfirmed data down.")
            downlink = decoded
            res = lorawan.mac_payload.get_fhdr().get_fctrl()
            if 0x20 & res != 0: # Check Ack bit.
                print("Server ack")
                if len(downlink) == 0:
                    downlink = "Server ack"
        elif lorawan.get_mhdr().get_mtype() == MHDR.CONF_DATA_DOWN:
            print("Confirmed data down.")
            self.ack = True
            downlink = decoded            
        elif lorawan.get_mhdr().get_mtype() == MHDR.CONF_DATA_UP:
            print("Confirmed data up.")
            downlink = decoded                        
        else:
            print("Other packet.")
            downlink = ''
        self.set_mode(MODE.STDBY)
        s = ''
        s += " pkt_snr_value  %f\n" % self.get_pkt_snr_value()
        s += " pkt_rssi_value %d\n" % self.get_pkt_rssi_value()
        s += " rssi_value     %d\n" % self.get_rssi_value()
        s += " msg: %s" % downlink
        print(s)

    def increment(self):
        self.tx_counter += 1
        data_file = open("frame.txt", "w")
        data_file.write(f'frame = {self.tx_counter:d}\n')
        data_file.close()

    def tx(self, msg, conf=False):
        if conf:
            data = MHDR.CONF_DATA_UP
            print('Sending confirmed data up.')
        else:
            data = MHDR.UNCONF_DATA_UP
            print('Sending unconfirmed data up.')            
        self.increment()
        lorawan = LoRaWAN.new(self.keys["nwskey"], self.keys["appskey"])
        base = {'devaddr': self.keys["devaddr"], 'fcnt': self.tx_counter, 'data': list(map(ord, msg))}
        if self.ack:
            print('Sending with Ack')
            lorawan.create(data, dict(**base, **{'ack':True}))
            self.ack = False
        else:
            print('Sending without Ack')
            lorawan.create(data, base)
        print(f"tx: {lorawan.to_raw()}")
        self.write_payload(lorawan.to_raw())
        self.set_mode(MODE.TX)

    def set_frame(self,frame):
        self.tx_counter = frame

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

    def on_tx_done(self):
        self.clear_irq_flags(TxDone=1)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0,0,0,0,0,0])
        self.set_freq(helium_helper.DOWNFREQ)
        self.set_bw(9)
        self.set_spreading_factor(7)
        self.set_pa_config(pa_select=1)
        self.set_rx_crc(False)
        self.set_invert_iq(1)
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)

    def transact(self, msg):
        self.setup_tx()
        self.tx(json.dumps({"i": self.iter, "s": self.uuid, "m": msg}), True)
        self.iter = self.iter+1
        self.last_tx = datetime.datetime.now()
        while self.last_message is None and (datetime.datetime.now() - self.last_tx).seconds < self.transact_timeout:
            sleep(0.1)
        return self.last_message

    def stop(self):
        self.set_mode(MODE.SLEEP)
        BOARD.teardown()

    def init_frame(self):
        frame = 0
        if os.path.exists('frame.txt'):
            with open('frame.txt') as df:
                for line in df:
                    if m := re.match('^frame\s*=\s*(\d+)', line):
                        frame = int(m.group(1))
        self.set_frame(frame)

    @classmethod
    def init(cls, verbose=False, keys=keys.get_keys()):
        BOARD.setup()
        lora = cls(verbose, keys)
        lora.init_frame()
        return lora
