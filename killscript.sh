#!/bin/bash
FPATH="/home/yulivee/Dokumente/Speicher- und Datennetze im IoT/Labor/mqtt-qos-rountrip"
PID_A=`cat "$FPATH"/client1.pid`
PID_B=`cat "$FPATH"/client2.pid`

kill -SIGUSR2 $PID_A;
kill -SIGUSR2 $PID_B;
sleep 3;
kill -SIGTERM $PID_A;
kill -SIGTERM $PID_B;

