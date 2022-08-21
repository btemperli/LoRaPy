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

import helium
import keys
BOARD.setup()
class HeliumLoRa(LoRa):
    def __init__(self, verbose = False, ack=True, start_ping=False):
        super(HeliumLoRa, self).__init__(verbose)
        self.iter = 0
        self.uuid = shortuuid.uuid()
        self.ack = ack
        self.test_status = {"running_ping": start_ping, "ping_count": 0, "last_message": None}
        self.last_tx = datetime.datetime.fromtimestamp(0)
        self.last_message = None
        self.transact_timeout = 5
        self.is_otaaing = False

    def otaa(self):
        print(self)
        self.is_otaaing = True
        self.setup_tx()
        lorawan = LoRaWAN.new(keys.appkey)
        devnonce = [randrange(256), randrange(256)]
        lorawan.create(MHDR.JOIN_REQUEST, {'deveui': keys.deveui, 'appeui': keys.appeui, 'devnonce': devnonce})
        self.write_payload(lorawan.to_raw())
        self.set_mode(MODE.TX)
        sleep(10)

    def on_rx_done(self):
        print("RxDone")
        import code;code.interact(local=dict(globals(), **locals())) 
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        if self.is_otaaing:
            self.set_mode(MODE.SLEEP)
            self.get_all_registers()
            print(self)
            lorawan = LoRaWAN.new([], keys.appkey)
            lorawan.read(payload)
            print(lorawan.get_payload())
            print(lorawan.get_mhdr().get_mversion())
            if lorawan.get_mhdr().get_mtype() == MHDR.JOIN_ACCEPT:
                print("Got LoRaWAN join accept. Paste these values into keys.py")
                print(lorawan.valid_mic())
                devaddr = lorawan.get_devaddr()
                print("devaddr = {devaddr}".format())
                nwskey = lorawan.derive_nwskey(devnonce)
                print("nwskey = {nwskey}".format())
                appskey = lorawan.derive_appskey(devnonce)
                print("appskey = {appskey}".format())
                print("\n")
            self.is_otaaing = False
            self.otaa_result = [devaddr, nwskey, appskey]
        else:
            print("Raw payload: {}".format(payload))
            lorawan = LoRaWAN.new(keys.nwskey, keys.appskey)
            decoded = "".join(list(map(chr, lorawan.get_payload())))
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
        lorawan = LoRaWAN.new(keys.nwskey, keys.appskey)
        base = {'devaddr': keys.devaddr, 'fcnt': self.tx_counter, 'data': list(map(ord, msg))}
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
        # Setup
        # self.set_mode(MODE.SLEEP)
        # self.set_dio_mapping([1,0,0,0,0,0])
        # self.set_freq(helium.UPFREQ)
        # if not self.is_otaaing:
        #     self.set_bw(7)
        # else:
        #     self.set_pa_config(pa_select=1)
        # self.set_spreading_factor(7)
        # self.set_pa_config(max_power=0x0F, output_power=0x0E)
        # self.set_sync_word(0x34)
        # self.set_rx_crc(True)
        # if not self.is_otaaing:
        #     self.set_invert_iq(0)
        # else:
        #     self.get_all_registers()
        # assert(self.get_agc_auto_on() == 1)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([1,0,0,0,0,0])
        self.set_freq(helium.UPFREQ)
        self.set_pa_config(pa_select=1)
        self.set_spreading_factor(7)
        self.set_pa_config(max_power=0x0F, output_power=0x0E)
        self.set_sync_word(0x34)
        self.set_rx_crc(True)
        self.get_all_registers()
        print(self)
        assert(self.get_agc_auto_on() == 1)

    def on_tx_done(self):
        self.clear_irq_flags(TxDone=1)
        print("TxDone")
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0,0,0,0,0,0])
        self.set_invert_iq(1)
        self.reset_ptr_rx()
        self.set_freq(helium.DOWNFREQ)#915)        
        self.set_spreading_factor(7)#12)
        self.set_bw(9) #500Khz
        self.set_rx_crc(False)#TRUE
        self.set_mode(MODE.RXCONT)
        # self.clear_irq_flags(TxDone=1)
        # self.set_mode(MODE.SLEEP)
        # self.set_dio_mapping([0,0,0,0,0,0])
        # self.set_freq(helium.DOWNFREQ)
        # self.set_bw(9)
        # self.set_spreading_factor(7)
        # self.set_pa_config(pa_select=1)
        # if not self.is_otaaing:
        #     self.set_sync_word(0x34)
        # self.set_rx_crc(False)
        # self.set_invert_iq(1)
        # self.reset_ptr_rx()
        # self.set_mode(MODE.RXCONT)

    def transact(self, msg):
        self.setup_tx()
        self.tx(json.dumps({"i": self.iter, "s": self.uuid, "m": msg}))
        self.iter = self.iter+1
        self.last_tx = datetime.datetime.now()
        while self.last_message is None and (datetime.datetime.now() - self.last_tx).seconds > self.transact_timeout:
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
    def init(cls, verbose=False, ack=True, start_ping=False):
        lora = cls(verbose, ack, start_ping)
        lora.init_frame()
        return lora
