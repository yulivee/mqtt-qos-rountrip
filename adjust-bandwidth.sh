#!/bin/bash
SPEED="10kbps"
IFACE="enp0s25"

#show current rules
tc class show dev $IFACE

#clear all tc rules
sudo tc qdisc del dev $IFACE root

#throttle
sudo tc qdisc add dev $IFACE handle 1: root htb default 11
sudo tc class add dev $IFACE parent 1: classid 1:1 htb rate $SPEED
sudo tc class add dev $IFACE parent 1:1 classid 1:11 htb rate $SPEED

#show current rules
tc class show dev $IFACE
