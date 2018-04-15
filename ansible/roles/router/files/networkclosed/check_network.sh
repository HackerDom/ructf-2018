#!/bin/bash

iptables -C FORWARD -s 10.60.0.0/17 -d 10.60.0.0/17 -j DROP  &> /dev/null
NETOPENED=$?

if [[ $NETOPENED == 1 ]]; then
  echo Network is opened  
  
  for num in {1..32}; do
    ip="10.60.$num.254"
    iptables -t nat -w -C PREROUTING -i eth0.$((num+100)) -d 10.60.0.0/17 -p tcp -m tcp -m comment --comment closednetwork -j DNAT --to-destination ${ip}:40002 &> /dev/null
    if [[ $? == 0 ]]; then
      echo "Warning: DNAT record still exists for team ${num}"
    fi
  done
   
else
  echo Network is closed

  for num in {1..32}; do
    ip="10.60.$num.254"
    iptables -t nat -w -C PREROUTING -i eth0.$((num+100)) -d 10.60.0.0/17 -p tcp -m tcp -m comment --comment closednetwork -j DNAT --to-destination ${ip}:40002 &> /dev/null
    if [[ $? != 0 ]]; then
      echo "Warning: no DNAT record for team ${num}"
    fi
  done
fi

if ! iptables -C FORWARD -s 10.60.0.0/17 -d 10.60.0.0/17 -p tcp --dport 22 -j DROP &> /dev/null; then
    echo "Warning: port 22 is not filtered"
fi
