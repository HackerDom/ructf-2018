#!/bin/bash
# checks rules for teams snat. Team will see incoming connections from 10.60.{1..32}.254
# this script should be run once before the game starts

for num in {1..32}; do 
    ip="10.60.$num.254"

    if ! iptables -t nat -C POSTROUTING -o eth0.$((num+100)) -j SNAT --to-source ${ip}; then
        echo "Holy sheet! Team ${num} is not SNATted!!!"
        echo "You can fix it with this command"
        echo "iptables -t nat -A POSTROUTING -o eth0.$((num+100)) -j SNAT --to-source ${ip}"
    fi
done
