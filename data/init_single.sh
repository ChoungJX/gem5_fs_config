#!/bin/bash

m5 workbegin
sleep 1
m5 readfile > /tmp/server
chmod 755 /tmp/server


ifconfig lo 127.0.0.1
/sbin/ifconfig -a

m5 workbegin
sleep 1
m5 readfile > /tmp/wrk
chmod 755 /tmp/wrk

echo "start to boot server"
nohup /tmp/server > /dev/null 2>&1 &

echo "test server status"
sleep 3
curl http://127.0.0.1:3000

echo "finished boot server"

echo "start to boot wrk"
/tmp/wrk -t1 -c200 -d1s http://127.0.0.1:3000