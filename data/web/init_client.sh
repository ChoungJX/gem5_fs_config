
service haveged start
# haveged -b 512
m5 workbegin

echo "load wrk"
m5 readfile > /tmp/workload
chmod 755 /tmp/workload

echo "set client ip"
/bin/hostname client
/sbin/ifconfig eth0 hw ether 00:90:00:00:00:06
/sbin/ifconfig eth0 192.168.0.6 netmask 255.255.255.0 up
/sbin/ifconfig -a

echo "ping server test"
ping 192.168.0.4 -c 3


echo "wait for server to start, sleep 3s"
sleep 3

echo "start to test server connection"
curl http://192.168.0.4:3000/user/get/random
echo "finished curl test"

sleep 1
echo "start to run wrk"

/tmp/workload -t8 -c800 -d1s http://192.168.0.4:3000/user/get/random
m5 exit 1
m5 exit 0