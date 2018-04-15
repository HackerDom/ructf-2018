#!/bin/bash

# go to script dir 
cd "$( dirname "${BASH_SOURCE[0]}" )"

if ! iptables -C FORWARD -s 10.60.0.0/17 -d 10.60.0.0/17 -j DROP &> /dev/null; then
    iptables -I FORWARD 1 -s 10.60.0.0/17 -d 10.60.0.0/17 -j DROP
fi

if ! iptables -C FORWARD -s 10.60.0.0/17 -d 10.60.0.0/17 -p tcp --dport 22 -j DROP &> /dev/null; then
    iptables -I FORWARD 1 -s 10.60.0.0/17 -d 10.60.0.0/17 -p tcp --dport 22 -j DROP
fi

for num in {1..32}; do
    ip="10.60.$num.254"

    if ! iptables -t nat -C PREROUTING -i eth0.$((num+100)) -d 10.60.0.0/17 -p tcp -m tcp -m comment --comment closednetwork -j DNAT --to-destination ${ip}:40002 &> /dev/null; then
        iptables -t nat -A PREROUTING -i eth0.$((num+100)) -d 10.60.0.0/17 -p tcp -m tcp -m comment --comment closednetwork -j DNAT --to-destination ${ip}:40002 &> /dev/null
        #echo "Added DNAT rule for team ${num}"
    fi
done

./check_network.sh
