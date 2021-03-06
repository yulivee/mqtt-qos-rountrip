#!/usr/bin/python
import paho.mqtt.client as mqtt
import time
import logging
import re
import signal
import os

logger = logging.getLogger(__name__)
handler = ""
broker_address="192.168.1.115"
port=1883
client_name="Stolz"
qos_level=""
topic=""

def read_topic():	
    global topic
    while ( not os.path.isfile('topic.ipc') ):
        pass
    f = open('topic.ipc', 'r')
    topic = f.read()
    print "[client2]{read_topic} topic from file: "+topic
    return topic

def signal_handler(a,b):
    print "[client2]{signal_handler} signal "+str(a)+" received, READING TOPIC"
    read_topic()

def signal_handler_2(a,b):
    print "[client2]{signal_handler_2} signal "+str(a)+" received, DISCONNECTING"
    client.loop_stop() #stop the loop
    client.disconnect()
    os.remove('client2.pid')

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
    formatter = logging.Formatter(fmt='%(asctime)s:%(msecs)03d,%(message)s',datefmt='%Y-%m-%d,%H:%M:%S')
    handler.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(handler)
    return logger

def subscribe(client,topic,qos_level):
    print("[client2]{subscribe} subscribing to topic"+topic)
    sub_rc = client.subscribe(topic,int(qos_level))
    print("[client2]{subscribe} subscribe returned "+str(sub_rc))
    wait_for(client, sub_rc)

def on_message(client, userdata, message):
    counter = message.payload[:6]
    logger.info("received,"+message.topic+","+str(message.qos)+","+str(len(message.payload))+","+counter)
    publish_back(message.topic, message.payload, message.qos, message.mid, counter)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.connected_flag=True
	print("[client2]{on_connect} client connected to broker")
    else:
	print("[client2]{on_connect} client failed to connected to broker, Return Code = "+rc)
        client.loop_stop()

def on_disconnect(client, userdata, rc):
    print("[client2]{on_disconnect} client disconnected from broker")

def on_publish(client,userdata,mid):             #create function for callback
    pass

def on_log(client, userdata, level, buf):
    pass
    #print("log: ",buf)

def wait_for(client,msgType,period=0.25):
    if msgType=="SUBACK":
        if client.on_subscribe:
            while not client.suback_flag:
                print("[client2]{wait_for} waiting suback")
                client.loop()  #check for messages
                #time.sleep(period)

def publish_back(topic, payload, qos, mid, counter):
    topic=topic+"_2"
    pub_rc = client.publish(topic,payload, qos, False)
    if pub_rc[0] == 0:
           logger.info("sent,"+topic+","+str(qos_level) +","+str(len(payload))+","+str(counter).zfill(6))
    else:
           logger.info("fail,"+topic+","+str(qos_level) +","+str(len(payload))+","+str(counter).zfill(6))

signal.signal(signal.SIGUSR1,signal_handler);
signal.signal(signal.SIGUSR2,signal_handler_2);

with open('client2.pid', 'w') as the_file:
    the_file.write(str(os.getpid()))

while ( not os.path.isfile('client1.pid') ):
    pass

f = open('client1.pid','r')
client1_pid = f.read()
c1pid = int(client1_pid)

print "[client2] client1 pid: "+str(c1pid)

client = mqtt.Client(client_name) #create new client instance
#attach functions to callbacks
client.on_log=on_log
client.on_message=on_message 
client.on_publish=on_publish
client.on_connect=on_connect
client.on_disconnect=on_disconnect


# Connection to Broker
print("[client2] connecting to broker "+broker_address+":"+str(port))
rc = client.connect(broker_address,port) #connect to broker

#while( rc != 0 ):
#    time.sleep(0.5)
#    rc = client.connect(broker_address,port) #connect to broker
#    print "[client2] connect returned "+str(rc)

client.loop_start() #start the loop

while( topic == ""):
    pass

print "[client2] topic "+topic
qos_level = get_qos(topic)
logname = get_logname(topic)
logger = get_logger(logname)
subscribe(client,topic,qos_level)

print "[client2] sending client1 the signal to start sending"
os.kill(c1pid,signal.SIGUSR1)

while ( 1 ):
    pass
