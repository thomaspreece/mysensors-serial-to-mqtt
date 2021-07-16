# mysensors-serial-to-mqtt

This is a simple script that takes messages from a Serial mysensors gateway and pushes them to MQTT. Similarly it takes messages from MQTT and pushes them to the Serial mysensors gateway.

This is useful if you want to use a simple mysensors serial gateway but have the ability to have another system push firmware updates to the nodes by connecting to MQTT

To install dependencies run:
```
pip install -r requirements.txt
```

To run the serial-to-mqtt script run

```
python3 ./serial_to_mqtt.py
```
