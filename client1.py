#!/usr/bin/python
import paho.mqtt.client as mqtt
import time
import logging
import argparse
import re
import os
import signal

parser = argparse.ArgumentParser()
parser.add_argument('--qos_level', type=int, help="qos_level to be used" , choices=[0, 1, 2], default=0)
parser.add_argument('--file', help="the file to be sent in the mqtt-message", default="empty")
parser.add_argument('--time', type=int, help="time in minutes to send packages")
parser.add_argument('--cycles', type=int, help="number of times a packet should be sent")
args = parser.parse_args()

f=args.file
qos_level=args.qos_level
logname="mqtt-roundtrip-"
logname=logname+ "qos"+str(args.qos_level)+"-"
message=""

if f== "empty":
   logname=logname+"empty_message"
else:
   match = re.search(r'files/(.*).txt',args.file)
   name = match.group(1)
   logname=logname+name
   f = open(args.file)
   filecontent = f.read()
   message = bytearray(filecontent)

if args.time:
   logname=logname+"-"+str(args.time)+"-minutes"

if args.cycles:
   logname=logname+"-"+str(args.cycles)+"-cycles"

topic=logname
logname=logname+"-client1.log"

print "[client1] ---------- "+topic+" ----------"

with open('topic.ipc', 'w') as the_file:
    the_file.write(topic)

f = open('client2.pid','r')
client2_pid = f.read()
pid = int(client2_pid)
os.kill(pid, signal.SIGUSR1)

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
    counter=message.payload[:6]
    logger.info("message received - topic:"+message.topic+" - qos:"+str(message.qos)+" - size:"+str(len(message.payload))+" - id:"+counter)

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
    pass

def on_log(client, userdata, level, buf):
    pass
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
answer_topic=topic+"_2"

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
logger.info("subscribe returned "+str(sub_rc))
wait_for(client, sub_rc)
 
counter = 0
max_counter = 100000

if args.cycles:
   logger.info("Performing message publishing for "+str(args.cycles)+" cycles")
   i=args.cycles
   while (i!=0) :
       pub_rc = client.publish(topic,str(counter).zfill(6)+message, qos_level, False)
       if pub_rc[0] == 0:
           logger.info("message sent - topic:"+topic+" - qos:"+str(qos_level) +" - id:"+str(counter).zfill(6))
       else:
           logger.info("message publish failed for message "+str(counter).zfill(6))
       if counter < max_counter:
           counter = counter + 1
       else:
           counter = 0
       i=i-1

if args.time:
   logger.info("Performing message publishing for "+str(args.time)+" minutes")
   starttime = time.time()
   stoptime = starttime + (args.time * 60);
   while ( time.time() < stoptime ) :	
       pub_rc = client.publish(topic,str(counter).zfill(6)+message, qos_level, False)
       if counter < max_counter:
           counter = counter + 1
       else:
           counter = 0


time.sleep(3); #wait 10 seconds for incoming messages
client.loop_stop() #stop the loop
client.disconnect()
print "[client1] killing client2"
os.kill(pid, signal.SIGTERM)
