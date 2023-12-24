# """Example for using pymysensors with mqtt."""
import paho.mqtt.client as mqtt  # pylint: disable=import-error
import time
import mysensors.mysensors as mysensors
from dotenv import load_dotenv

import logging
import sys
import os

import argparse

load_dotenv()

root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

PORT=os.environ["SERIAL_PORT"]
MQTT_USERNAME = os.environ["MQTT_USERNAME"]
MQTT_PASSWORD=os.environ["MQTT_PASSWORD"]
MQTT_SERVER=os.environ["MQTT_SERVER"]

in_prefix="mysensors-gateway-in"
out_prefix="mysensors-gateway-out"

parser = argparse.ArgumentParser()
parser.add_argument("update_filepath", help="Filepath to update hex file")
parser.add_argument("fw_type", help="fw_type (int)", type=int)
parser.add_argument("fw_version", help="fw_version (int)", type=int)
parser.add_argument("node_id", help="node_id (int)", type=int)
args = parser.parse_args()

class MQTT(object):
    """MQTT client example."""

    # pylint: disable=unused-argument

    def __init__(self, broker, port, keepalive):
        """Set up MQTT client."""
        self.topics = {}
        self._mqttc = mqtt.Client()
        self._mqttc.username_pw_set(USERNAME, password=MQTT_PASSWORD)
        self._mqttc.connect(broker, port, keepalive)

    def publish(self, topic, payload, qos, retain):
        """Publish an MQTT message."""
        self._mqttc.publish(topic, payload, qos, retain)

    def subscribe(self, topic, callback, qos):
        """Subscribe to an MQTT topic."""
        if topic in self.topics:
            return

        def _message_callback(mqttc, userdata, msg):
            """Run callback for received message."""
            callback(msg.topic, msg.payload.decode("utf-8"), msg.qos)

        self._mqttc.subscribe(topic, qos)
        self._mqttc.message_callback_add(topic, _message_callback)
        self.topics[topic] = callback

    def start(self):
        """Run the MQTT client."""
        print("Start MQTT client")
        self._mqttc.loop_start()

    def stop(self):
        """Stop the MQTT client."""
        print("Stop MQTT client")
        self._mqttc.disconnect()
        self._mqttc.loop_stop()


def mqtt_event(message):
    """Run callback for mysensors updates."""
    # print("sensor_update " + str(message.node_id))
    pass

MQTTC = MQTT(MQTT_SERVER, 1883, 60)
MQTTC.start()

MQTT_GATEWAY = mysensors.MQTTGateway(
    MQTTC.publish,
    MQTTC.subscribe,
    in_prefix=in_prefix,
    out_prefix=out_prefix,
    retain=True,
    event_callback=mqtt_event,
    protocol_version="2.3",
)

MQTT_GATEWAY.start()

print("Updating in 5s")
time.sleep(5)
print("Updating...")

MQTT_GATEWAY.update_fw(args.node_id, args.fw_type, args.fw_version, fw_path=args.update_filepath)

print("Complete")
while True:
    time.sleep(1)
