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
parser.add_argument('--pbs', type=int, help="packets per second")
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

if args.pbs:
   logname=logname+"-"+str(args.pbs)+"pbs"

topic=logname
logname=logname+"-client1.log"
start_sending = 0

print "[client1] ---------- "+topic+" ----------"

with open('topic.ipc', 'w') as the_file:
    the_file.write(topic)

with open('client1.pid', 'w') as the_file:
    the_file.write(str(os.getpid()))

print "[client1] own pid: "+str(os.getpid())

while ( not os.path.isfile('client2.pid') ):
    pass

f = open('client2.pid','r')
client2_pid = f.read()
pid = int(client2_pid)
os.kill(pid, signal.SIGUSR1)
print "[client1] client2 pid: "+str(pid)
print "[client1] sending client 2 signal to read topic"


logger = logging.getLogger(__name__)

# create a file handler
handler = logging.FileHandler('logs/'+logname)
handler.setLevel(logging.DEBUG)
logger.setLevel(logging.DEBUG)

# create a logging format
formatter = logging.Formatter(fmt='%(asctime)s:%(msecs)03d,%(message)s',datefmt='%Y-%m-%d,%H:%M:%S')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)

def signal_handler(a,b):
    print "[client1] signal "+str(a)+" received, START SENDING"
    global start_sending
    start_sending = 1

def signal_handler_2(a,b):
    print "[client1] signal "+str(a)+" received, DISCONNECTING"
    client.loop_stop() #stop the loop
    client.disconnect()

def on_message(client, userdata, message):
    counter=message.payload[:6]
    logger.info("received,"+message.topic+","+str(message.qos)+","+str(len(message.payload))+","+counter)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.connected_flag=True
	print("[client1] client connected to broker")
    else:
	print("[client1] client failed to connected to broker, Return Code = "+rc)
        client.loop_stop()

def on_disconnect(client, userdata, rc):
    print("[client1] client disconnected from broker")

def on_publish(client,userdata,mid):             #create function for callback
    pass

def on_log(client, userdata, level, buf):
    pass
    #print("log: ",buf)

def wait_for(client,msgType,period=0.25):
    if msgType=="SUBACK":
        if client.on_subscribe:
            while not client.suback_flag:
                print("waiting suback")
                client.loop()  #check for messages

signal.signal(signal.SIGUSR1,signal_handler);
signal.signal(signal.SIGUSR2,signal_handler_2);

#broker_address="192.168.1.115"
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
print("[client1] connecting to broker "+broker_address+":"+str(port))
client.connect(broker_address,port) #connect to broker
client.loop_start() #start the loop

print("[client1] subscribing to topic "+answer_topic)
sub_rc = client.subscribe(answer_topic,qos_level)
print("[client1] subscribe returned "+str(sub_rc))
wait_for(client, sub_rc)
 
counter = 0
max_counter = 999999

while ( start_sending != 1 ):
   pass

if args.cycles:
   print("[client1] performing message publishing for "+str(args.cycles)+" cycles")
   i=args.cycles
   while (i!=0) :
       time.sleep(0.005)
       pub_rc = client.publish(topic,str(counter).zfill(6)+message, qos_level, False)
       if pub_rc[0] == 0:
           logger.info("sent,"+topic+","+str(qos_level) +","+str(len(message))+","+str(counter).zfill(6))
       else:
           logger.info("fail,"+topic+","+str(qos_level) +","+str(len(message))+","+str(counter).zfill(6))
       if counter < max_counter:
           counter = counter + 1
       else:
           counter = 0
       i=i-1

if args.time:
   print("[client1] performing message publishing for "+str(args.time)+" minutes")
   starttime = time.time()
   stoptime = starttime + (args.time * 60);
   sleeptime = 0

   if ( args.pbs == 1 ):
       sleeptime = 1
   if ( args.pbs == 10 ):
       sleeptime = 0.1
   if ( args.pbs == 100 ):
       sleeptime = 0.1

   while ( time.time() < stoptime ) :	
       time.sleep(sleeptime)
       pub_rc = client.publish(topic,str(counter).zfill(6)+message, qos_level, False)
       if pub_rc[0] == 0:
           logger.info("sent,"+topic+","+str(qos_level) +","+str(len(message))+","+str(counter).zfill(6))
       else:
           logger.info("fail,"+topic+","+str(qos_level) +","+str(len(message))+","+str(counter).zfill(6))
           logger.info("discard,"+topic+","+str(qos_level) +","+str(len(message))+","+str(counter).zfill(6))
       if counter < max_counter:
           counter = counter + 1
       else:
           counter = 0

print "DONE SENDING - Grace time waiting"

time.sleep(10); #wait 10 seconds for incoming messages
client.loop_stop() #stop the loop
client.disconnect()
print "[client1] sending client2 disconnect signal"
os.kill(pid, signal.SIGUSR2)
time.sleep(1)
print "[client1] killing client2"
os.kill(pid, signal.SIGTERM)
os.remove('client1.pid')
os.remove('topic.ipc')
