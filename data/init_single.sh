#!/bin/bash

service haveged start
m5 workbegin

echo "load server binary"
m5 readfile > /tmp/server
chmod 755 /tmp/server

echo "set server ip"
ifconfig lo 127.0.0.1
/sbin/ifconfig -a

echo "load wrk"
m5 workbegin
m5 readfile > /tmp/wrk
chmod 755 /tmp/wrk

m5 workbegin
echo "load database file"
m5 readfile > /root/hello_world.db

echo "start to boot server"
DATABASE_URL=/root/hello_world.db nohup /tmp/server > /dev/null 2>&1 &

echo "test server status"
curl http://127.0.0.1:3000

echo "finished boot server"

echo "start to boot wrk"
/tmp/wrk -t1 -c200 -d1s http://127.0.0.1:3000