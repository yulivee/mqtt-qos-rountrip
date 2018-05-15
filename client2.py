#!/usr/bin/python
import paho.mqtt.client as mqtt
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# create a file handler
handler = logging.FileHandler('client2.log')
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)


def on_message(client, userdata, message):
    logger.info("message received - id:"+message.id+" - topic:"+message.topic+" - qos:"+message.qos+" - size:"+str(len(message.payload)))
    publish_back(message.topic, message.payload, message.qos, message.id)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.connected_flag=True
	logger.info("Client connected to broker")
    else:
	logger.info("Client failed to connected to broker, Return Code = ", rc)
        client.loop_stop()

def on_disconnect(client, userdata, rc):
    logger.info("Client disconnected from broker")

def on_publish(client,userdata,mid):             #create function for callback

def on_log(client, userdata, level, buf):
    #print("log: ",buf)

def wait_for(client,msgType,period=0.25):
    if msgType=="SUBACK":
        if client.on_subscribe:
            while not client.suback_flag:
                logging.info("waiting suback")
                client.loop()  #check for messages
                time.sleep(period)

def publish_back(topic, payload, qos, mid):
    topic=topic+"_2"
    pub_rc = client.publish(topic,payload, qos_level, False)
    logger.info("message sent - id:"+mid+" - topic:"+topic+" - qos:"+qos_level+" - size:"+str(len(payload)))

broker_address="192.168.1.100"
port=1883
qos_level=0
client_name="Stolz"
topic="test"

print("creating new instance "+client_name)
client = mqtt.Client(client_name) #create new client instance
#attach functions to callbacks
client.on_log=on_log
client.on_message=on_message 
client.on_publish=on_publish
client.on_connect=on_connect
client.on_disconnect=on_disconnect

# Connection to Broker
logger.info("connecting to broker "+broker_address+":"+str(port))
client.connect(broker_address,port) #connect to broker
client.loop_start() #start the loop


logger.info("Subscribing to topic",topic)
sub_rc = client.subscribe("test",qos_level)
logger.info("subscribe returned ",sub_rc)
wait_for(client, sub_rc)

while ( 1 ):
    pass

client.loop_stop() #stop the loop
