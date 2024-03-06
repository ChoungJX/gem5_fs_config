#!/bin/bash

./build/ARM/gem5.fast -d m5out/switch configs/dist/sw.py --is-switch --checkpoint-dir=m5out/switch --dist-server-port=2200 --dist-size=21 --dist-sync-repeat="10us" --dist-sync-start="1000000000000t"
