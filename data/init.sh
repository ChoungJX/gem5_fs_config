#!/bin/bash

m5 checkpoint 1
sleep 2

m5 workbegin
sleep 1
m5 readfile > /tmp/workload
chmod 755 /tmp/workload

m5 workbegin
sleep 1
m5 readfile > /tmp/run.sh
chmod 755 /tmp/run.sh
/tmp/run.sh