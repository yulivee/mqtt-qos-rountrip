#!/usr/bin/python
import paho.mqtt.client as mqtt
import time
import logging
import re
import signal
import os

logger = logging.getLogger(__name__)
handler = ""
broker_address="192.168.1.100"
port=1883
client_name="Stolz"
qos_level=""
topic=""

def init_new_connection():
    global topic
    global qos_level
    global logger
    global handler
    if 'logger' in globals():
        logger = ""
        handler = ""
    topic = read_topic()
    qos_level = get_qos(topic)
    logname = get_logname(topic)
    logger = get_logger(logname)
    subscribe(topic,qos_level)

def signal_handler(a,b):
    print "[client2] signal "+str(a)+" received"
    init_new_connection()

def read_topic():	
    f = open('topic.ipc', 'r')
    topic = f.read()
    print "[client2] topic "+topic
    return topic

def get_qos(topic):
    match = re.search(r'-qos(\d)-',topic)
    qos_level=match.group(1)
    return qos_level
   
def get_logname(topic):
    logname=topic+'-client2.log'
    return logname

def get_logger(logname):
    logger = logging.getLogger(__name__)
    # create a file handler
    global handler
    handler = logging.FileHandler('logs/'+logname)
    handler.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    # create a logging format
    formatter = logging.Formatter(fmt='%(asctime)s:%(msecs)03d- %(message)s',datefmt='%Y-%m-%d_%H:%M:%S')
    handler.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(handler)
    return logger


def subscribe(topic,qos_level):
    logger.info("Subscribing to topic"+topic)
    sub_rc = client.subscribe(topic,int(qos_level))
    logger.info("subscribe returned "+str(sub_rc))
    wait_for(client, sub_rc)

def on_message(client, userdata, message):
    counter = message.payload[:6]
    logger.info("message received - topic:"+message.topic+" - qos:"+str(message.qos)+" - size:"+str(len(message.payload))+" - id:"+counter)
    publish_back(message.topic, message.payload, message.qos, message.mid, counter)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.connected_flag=True
	print("Client connected to broker")
    else:
	print("Client failed to connected to broker, Return Code = "+rc)
        client.loop_stop()

def on_disconnect(client, userdata, rc):
    logger.info("Client disconnected from broker")

def on_publish(client,userdata,mid):             #create function for callback
    pass

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

def publish_back(topic, payload, qos, mid, counter):
    topic=topic+"_2"
    pub_rc = client.publish(topic,payload, qos, False)
    if pub_rc[0] == 0:
        logger.info("message sent - topic:"+topic+" - qos:"+str(qos_level) +" - id:"+counter)
    else:
        logger.info("message publish failed for message "+counter)


signal.signal(signal.SIGUSR1,signal_handler);

with open('client2.pid', 'w') as the_file:
    the_file.write(str(os.getpid()))

client = mqtt.Client(client_name) #create new client instance
#attach functions to callbacks
client.on_log=on_log
client.on_message=on_message 
client.on_publish=on_publish
client.on_connect=on_connect
client.on_disconnect=on_disconnect

# Connection to Broker
print("[client2] connecting to broker "+broker_address+":"+str(port))
client.connect(broker_address,port) #connect to broker
client.loop_start() #start the loop



while ( 1 ):
    pass

client.loop_stop() #stop the loop
client.disconnect()
