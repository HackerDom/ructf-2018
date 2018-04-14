#!/bin/bash
# removes rules for teams snat
# this script shouldn't be run normally :)

for num in {1..32}; do 
    ip="10.60.$num.254"

    iptables -t nat -D POSTROUTING -o eth0.$((num+100)) -j SNAT --to-source ${ip}
done
