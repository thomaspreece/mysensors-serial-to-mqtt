from mysensors import Message
from serial import serial_for_url
from serial.serialutil import SerialException
from serial.threaded import LineReader, ReaderThread
from dotenv import load_dotenv
import sys
import time
import traceback
import paho.mqtt.client as mqtt  # pylint: disable=import-error
import logging
import os 

load_dotenv()

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

_mqttc = mqtt.Client()
_mqttc.username_pw_set(os.environ["MQTT_USERNAME"], password=os.environ["MQTT_PASSWORD"])
_mqttc.connect(os.environ["MQTT_SERVER"], 1883, 60)
_mqttc.loop_start()

in_prefix="mysensors-gateway-in"
out_prefix="mysensors-gateway-out"

PORT=os.environ["SERIAL_PORT"]
BAUD=int(os.environ["BAUD"])
DEBUG=(os.environ["DEBUG"] == "True")

def parse_mqtt_to_message(topic, payload, qos):
    """Parse a MQTT topic and payload.
    Return a mysensors command string.
    """
    # pylint: disable=no-self-use
    topic_levels = topic.split("/")
    topic_levels = not_prefix = topic_levels[-5:]
    prefix_end_idx = topic.find("/".join(not_prefix)) - 1
    prefix = topic[:prefix_end_idx]
    if prefix != out_prefix:
        return None
    if qos and qos > 0:
        ack = "1"
    else:
        ack = "0"
    topic_levels[3] = ack
    topic_levels.append(str(payload))
    return ";".join(topic_levels)

def parse_message_to_mqtt(data):
    """Parse a mysensors command string.
    Return a MQTT topic, payload and qos-level as a tuple.
    """
    msg = Message(data)
    payload = str(msg.payload)
    msg.payload = ""
    # prefix/node/child/type/ack/subtype : payload
    return f"/{msg.encode('/')}"[:-2], payload, msg.ack

class PrintLines(LineReader):
    TERMINATOR=b'\n'
    portClosed=False

    def connection_made(self, transport):
        super(PrintLines, self).connection_made(transport)
        logging.info('Port Opened {}'.format(PORT))

    def handle_line(self, data):
        topic, payload, ack = parse_message_to_mqtt(str(data))
        topic = str(in_prefix) + str(topic)
        _mqttc.publish(topic, payload, ack, True)
        logging.debug('R: {}\n'.format(repr(data)))

    def connection_lost(self, exc):
        self.portClosed=True
        logging.info('Port closed {}'.format(PORT))

while(True):
    try:
        ser = serial_for_url(PORT, baudrate=BAUD, timeout=1)
        with ReaderThread(ser, PrintLines) as protocol:
            def on_mqtt_message(client, userdata, message):
                mymessage = parse_mqtt_to_message(message.topic, message.payload.decode('ascii'), message.qos)
                if mymessage != None:
                    protocol.write_line(str(mymessage))
                    if DEBUG:
                        logging.debug('S: {}'.format(str(mymessage)))

            _mqttc.subscribe(out_prefix + "/#")
            _mqttc.on_message = on_mqtt_message

            while(not protocol.portClosed):
                time.sleep(1)

    except SerialException as error:
        logging.warning('Failed to Connect to Serial Port: {}'.format(PORT))
        time.sleep(5)
