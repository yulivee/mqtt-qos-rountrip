#!/bin/bash
PID_A=$(cat ./client1.pid)
PID_B=$(cat ./client2.pid)

kill -SIGUSR2 $PID_A;
kill -SIGUSR2 $PID_B;
sleep 3;
kill -SIGTERM $PID_A;
kill -SIGTERM $PID_B;

