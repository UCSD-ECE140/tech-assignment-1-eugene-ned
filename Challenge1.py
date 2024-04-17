import paho.mqtt.client as paho
from paho import mqtt
import time
import random

def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)

def on_publish(client, userdata, mid, properties=None):
    print("mid: " + str(mid))

def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_message(client, userdata, msg):
    print(f"Message received on topic {msg.topic}: {str(msg.payload.decode())}")

client_sub = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1,client_id="276934ffc72b42bcb7e305f7d5676e58", protocol=paho.MQTTv5)
client_sub.on_connect = on_connect
client_sub.on_subscribe = on_subscribe
client_sub.on_message = on_message

client_sub.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
client_sub.username_pw_set("eugene", "Iqiq4pir&95977")
client_sub.connect("276934ffc72b42bcb7e305f7d5676e58.s1.eu.hivemq.cloud", 8883)

# Subscribe to the topics
client_sub.subscribe("topic/publisher1", qos=1)
client_sub.subscribe("topic/publisher2", qos=1)

def subscriber_loop():
    while True:
        client_sub.loop(timeout=1.0)  

def create_publisher(client_id, topic):
    client_pub = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1,client_id="276934ffc72b42bcb7e305f7d5676e58", protocol=paho.MQTTv5)
    client_pub.on_connect = on_connect
    client_pub.on_publish = on_publish

    client_pub.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    client_pub.username_pw_set("eugene", "Iqiq4pir&95977")
    client_pub.connect("276934ffc72b42bcb7e305f7d5676e58.s1.eu.hivemq.cloud", 8883)
    client_pub.loop_start()

    while True:
        time.sleep(3)
        message = random.randint(1, 100)
        client_pub.publish(topic, payload=str(message), qos=1)

# Create and start publisher threads
from threading import Thread

publisher1_thread = Thread(target=create_publisher, args=("publisher1", "topic/publisher1"))
publisher2_thread = Thread(target=create_publisher, args=("publisher2", "topic/publisher2"))

publisher1_thread.start()
publisher2_thread.start()

# Start the subscriber loop
subscriber_loop()
