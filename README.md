# mysensors-serial-to-mqtt

This is a simple script that takes messages from a Serial mysensors gateway and pushes them to MQTT. Similarly it takes messages from MQTT and pushes them to the Serial mysensors gateway.

This is useful if you want to use a simple mysensors serial gateway but have the ability to have another system push firmware updates to the nodes by connecting to MQTT

## Create Python venv
```
apt-get install python3-venv
python3 -m venv mysensors
source mysensors/bin/activate
```

## Install Dependencies 

To install dependencies run:
```
pip install -r requirements.txt
```

## Run 

To run the serial-to-mqtt script run
```
python ./serial_to_mqtt.py
```
