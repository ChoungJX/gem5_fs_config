export ACTIX_TECHEMPOWER_MONGODB_URL="mongodb://192.168.0.5:27017"
m5 workbegin
sleep 1
m5 readfile > /tmp/workload
chmod 755 /tmp/workload

/bin/hostname client
/sbin/ifconfig eth0 hw ether 00:90:00:00:00:06
/sbin/ifconfig eth0 192.168.0.6 netmask 255.255.255.0 up
/sbin/ifconfig -a

sleep 5
echo "finish"
sleep 1000
curl http://192.168.0.4:8080/fortunes