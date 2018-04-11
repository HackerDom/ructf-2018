#!/bin/bash -e

TEAM=${1?Usage: open_network.sh <team>}

if ! [[ $TEAM =~ ^[0-9]+$ ]]; then
 echo "Team shold be integer"
 exit 1
fi

while iptables -w -C FORWARD -o "eth0.$((TEAM+100))" -j DROP &>/dev/null; do
  iptables -w -D FORWARD -o "eth0.$((TEAM+100))" -j DROP
done
