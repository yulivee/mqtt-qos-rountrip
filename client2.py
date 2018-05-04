#!/usr/bin/python
import paho.mqtt.client as mqtt
import time

def on_message(client, userdata, message):
    print("message received " ,str(message.payload.decode("utf-8")))
    print("message topic=",message.topic)
    print("message qos=",message.qos)
    print("message retain flag=",message.retain)
    
    publish_back(message.topic, message.payload, message.qos)

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

def publish_back(topic, payload, qos):
    topic=topic+"_2"
    print("publish message Hello World! on topic test, qos_level="+str(qos_level))
    pub_rc = client.publish(topic,payload, qos_level, False)
    print("publish returned ",pub_rc)

broker_address="192.168.1.100"
port=1883
qos_level=0
client_name="Stolz"

print("creating new instance "+client_name)
client = mqtt.Client(client_name) #create new client instance
#attach functions to callbacks
client.on_log=on_log
client.on_message=on_message 
client.on_publish=on_publish
client.on_connect=on_connect
client.on_disconnect=on_disconnect

# Connection to Broker
print("connecting to broker "+broker_address+":"+str(port))
client.connect(broker_address,port) #connect to broker
client.loop_start() #start the loop

#while not client.connected_flag:
#    print("waiting for connect")
#    time.sleep(2)
 

print("Subscribing to topic","test")
sub_rc = client.subscribe("test",qos_level)
print("subscribe returned ",sub_rc)
wait_for(client, sub_rc)

while ( 1 ):
    pass

client.loop_stop() #stop the loop
