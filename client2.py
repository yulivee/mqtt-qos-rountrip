#!/usr/bin/python
import paho.mqtt.client as mqtt
import time

def on_message(client, userdata, message):
    print("message received " ,str(message.payload.decode("utf-8")))
    print("message topic=",message.topic)
    print("message qos=",message.qos)
    print("message retain flag=",message.retain)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.connected_flag=True
        print("OK - connected")
    else:
        print("NOT OK - Return Code = ",rc)
        client.loop_stop()

def on_disconnect(client, userdata, rc):
    print("OK - client disconnected")

def on_publish(client,userdata,mid):             #create function for callback
    print("data published, mid= ", mid)

def on_log(client, userdata, level, buf):
    print("log: ",buf)

def wait_for(client,msgType,period=0.25):
    if msgType=="SUBACK":
        if client.on_subscribe:
            while not client.suback_flag:
                logging.info("waiting suback")
                client.loop()  #check for messages
                time.sleep(period)

broker_address="192.168.1.100"
port=1833
qos_level="0"

print("creating new instance")
client = mqtt.Client("Stolz") #create new client instance
#attach functions to callbacks
client.on_log=on_log
client.on_message=on_message 
client.on_publish=on_publish
client.on_connect=on_connect
client.on_disconnect=on_disconnect


print("connecting to broker")
client.connect(broker_address,port) #connect to broker
client.loop_start() #start the loop

while not client.connected_flag:
    print("waiting for connect")
    time.sleep(2)
 
print("Publishing message to topic","test")
# publish(topic, payload=None, qos=0, retain=False)
pub_rc = client.publish("test","Hello World!", qos_level, False)
print("publish returned ",pub_rc)
time.sleep(4) # wait

print("Subscribing to topic","test2")
sub_rc = client.subscribe("test2",qos_level)
print("subscribe returned ",sub_rc)
wait_for(client, sub_rc)

client.loop_stop() #stop the loop
