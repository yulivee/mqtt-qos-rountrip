#!/bin/bash
LOSS="$1"
IFACE="enp0s25"

echo "setting $LOSS% packetloss on interface on $IFACE"

#show current rules
sudo iptables -L
sudo iptables -F
sudo iptables -A INPUT -m statistic --mode random --probability $LOSS -j DROP
sudo iptables -A OUTPUT -m statistic --mode random --probability $LOSS -j DROP
sudo iptables -L
