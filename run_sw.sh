#!/bin/bash
echo "use port: $1"
./build/ARM/gem5.fast -d m5out/switch configs/dist/sw.py --is-switch --checkpoint-dir=m5out/switch --dist-server-port=$1 --dist-size=2 --dist-sync-repeat="10us" --dist-sync-start="10t"
