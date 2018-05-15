#!/usr/bin/python
import paho.mqtt.client as mqtt
import time
import logging
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--qos_level', type=int, help="qos_level to be used" , choices=[0, 1, 2], default=0)
parser.add_argument('--file', help="the file to be sent in the mqtt-message", default="")
parser.add_argument('--time', type=int, help="time in minutes to send packages")
parser.add_argument('--cycles', type=int, help="number of times a packet should be sent")
args = parser.parse_args()

qos_level=args.qos_level
f=args.file
logname="mqtt-roundtrip-"
logname=logname+ "qos"+args.qos_level+"-"
if f== "":
   logname=logname+"empty_message-"
else:
   logname=logname+args.f+"-"

if args.time:
   logname=logname+args.time+"minutes-"

if args.cycles:
   logname=logname+args.cycles+"cycles-"

topic=logname
print "topic for client2:"+topic

logname=logname+"-client1.log"


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# create a file handler
handler = logging.FileHandler(logname)
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)


def on_message(client, userdata, message):
    logger.info("message received - id:"+message.id+" - topic:"+message.topic+" - qos:"+message.qos+" - size:"+str(len(message.payload)))

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
    logger.info("message sent - id:"+mid+" - topic:"+topic+" - qos:"+qos_level+" - size:"+str(len(message)))

def on_log(client, userdata, level, buf):
    #print("log: ",buf)

def wait_for(client,msgType,period=0.25):
    if msgType=="SUBACK":
        if client.on_subscribe:
            while not client.suback_flag:
                logging.info("waiting suback")
                client.loop()  #check for messages
                time.sleep(period)

broker_address="192.168.1.100"
client_name="Schuhmacher"
port=1883
#topic="test"
answer_topic=topic+"_2"

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

logger.info("Subscribing to topic "+answer_topic)
sub_rc = client.subscribe(answer_topic,qos_level)
logger.info("subscribe returned ",sub_rc)
wait_for(client, sub_rc)
 
if f == "":
   message = f
else:
   f= open("file")
   filecontent = f.read()
   message = bytearray(filecontent)


if args.cycles:
   logger.info("Performing message publishing for "+args.cycles+" cycles")
   i=args.cycles
   while (i!=0) :
       pub_rc = client.publish(topic,message, qos_level, False)
       i=i-1

   client.loop_stop() #stop the loop
   exit

if args.time:
   logger.info("Performing message publishing for "+args.time+" minutes")
   starttime = time.time()
   stoptime = starttime + (args.time * 60);
   while ( time.time() < stoptime ) :	
       pub_rc = client.publish(topic,message, qos_level, False)
   client.loop_stop() #stop the loop
   exit

client.loop_stop() #stop the loop
