#RPI install routine
```
sudo apt-get install -y tmux htop 
sudo pip3 install adafruit-circuitpython-ssd1306
sudo pip3 install adafruit-circuitpython-framebuf
sudo pip3 install adafruit-circuitpython-rfm9x
sudo pip3 install adafruit-circuitpython-gps
sudo pip3 install pycryptodome
sudo pip3 install shortuuid
sudo pip3 install python-dotenv
sudo apt-get install gpsd gpsd-clients
git clone git@github.com:DGaffney/LoRaWAN.git
```

# LoRaWAN
This is a LoRaWAN v1.0 implementation in python.

It uses: https://github.com/mayeranalytics/pySX127x

For reference on LoRa see: https://www.lora-alliance.org/portals/0/specs/LoRaWAN%20Specification%201R0.pdf

This fork adds support for the Adafruit LoRA Radio Bonnet with OLED - RFM95W @ 915MHZ.

It also allows you to connect as a client to the Helium Network.



## Installation

After forking the repo, install the python libs:

    pip3 install -r requirements.txt

## Credentials

The keys can be added to a `./.env` file:

```
deveui = 1234ASD432
appeui = 234ASD4321
appkey = 34ASD43210

devaddr = [00,11,22]
nwskey = [11,22,33]
appskey = [22,33,44]
```

They can also be passed as environment variables:

```
deveui=1234ASD432 python3 rssi_helium.py
```

## Registration

You must create a device on the Helium Console at https://console.helium.com/

After copying the device credentials (the first three in the `.env` file, above), run otaa_helium.py, which will get the final three credentials for the `.env` file.

Then you can run tx_helium.py to send messages by specifying the msg and the frame like this:

    python3 tx_helium.py --msg "Test" --frame 1

You can run rssi_helium.py which utilizes the OLED screen and buttons.

This will sent a tranmission when it starts and whenever you press the middle button.

The transmission is a confirmed data message so a response will be received if a hotspot is in range.

The message just sends with the same frame to prevent having to track that and since the up link data is not needed.

The script pulls the RSSI, the packet RSSI, and the SNR and displays it on the OLED.

[pi]: pi.jpg "pi"

![alt text][pi]

## TODO
Automatically track frame number. 
Automatically capture device registration info and put in keys.py.
