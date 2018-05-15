#!/usr/bin/python
import paho.mqtt.client as mqtt
import time
import logging
import re

f = open('topic.ipc', 'r')
topic = f.read()
print topic

logname=topic+'-client2.log'
match = re.search(r'-qos(\d)-',topic)
qos_level=match.group(1)

logger = logging.getLogger(__name__)

# create a file handler
handler = logging.FileHandler('logs/'+logname)
handler.setLevel(logging.DEBUG)
logger.setLevel(logging.DEBUG)

# create a logging format
formatter = logging.Formatter(fmt='%(asctime)s:%(msecs)03d- %(message)s',datefmt='%Y-%m-%d_%H:%M:%S')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)


def on_message(client, userdata, message):
    logger.info("message received - id:"+str(message.mid)+" - topic:"+message.topic+" - qos:"+str(message.qos)+" - size:"+str(len(message.payload)))
    publish_back(message.topic, message.payload, message.qos, message.mid)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.connected_flag=True
	logger.info("Client connected to broker")
    else:
	logger.info("Client failed to connected to broker, Return Code = "+rc)
        client.loop_stop()

def on_disconnect(client, userdata, rc):
    logger.info("Client disconnected from broker")

def on_publish(client,userdata,mid):             #create function for callback
    logger.info("message sent - id:"+str(mid)+" - topic:"+topic+" - qos:"+str(qos_level))

def on_log(client, userdata, level, buf):
    pass
    #print("log: ",buf)

def wait_for(client,msgType,period=0.25):
    if msgType=="SUBACK":
        if client.on_subscribe:
            while not client.suback_flag:
                logger.info("waiting suback")
                client.loop()  #check for messages
                time.sleep(period)

def publish_back(topic, payload, qos, mid):
    topic=topic+"_2"
    pub_rc = client.publish(topic,payload, qos_level, False)

broker_address="192.168.1.100"
port=1883
qos_level=0
client_name="Stolz"

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


logger.info("Subscribing to topic"+topic)
sub_rc = client.subscribe(topic,qos_level)
logger.info("subscribe returned "+str(sub_rc))
wait_for(client, sub_rc)

while ( 1 ):
    pass

client.loop_stop() #stop the loop
client.disconnect()
