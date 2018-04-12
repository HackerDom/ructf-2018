#!/bin/bash

if VBoxControl --nologo guestproperty get team; then
  echo "Cloud detected"
  TEAM="$(VBoxControl --nologo guestproperty get team|cut -d' ' -f 2)"
  echo "TEAM=$TEAM"

  echo "auto eth0" > /etc/network/interfaces.d/eth0.cfg
  echo "iface eth0 inet static" >> /etc/network/interfaces.d/eth0.cfg
  echo "dns-nameservers 8.8.8.8 8.8.4.4" >> /etc/network/interfaces.d/eth0.cfg
  echo "address 10.$((60 + TEAM / 256)).$((TEAM % 256)).1" >>  /etc/network/interfaces.d/eth0.cfg
  echo "netmask 255.255.255.0" >>  /etc/network/interfaces.d/eth0.cfg
  echo "gateway 10.$((60 + TEAM / 256)).$((TEAM % 256)).254" >>  /etc/network/interfaces.d/eth0.cfg
else
  echo "auto eth0" > /etc/network/interfaces.d/eth0.cfg
  echo "iface eth0 inet dhcp" >> /etc/network/interfaces.d/eth0.cfg
  echo "dns-nameservers 8.8.8.8 8.8.4.4" >> /etc/network/interfaces.d/eth0.cfg
fi

if VBoxControl --nologo guestproperty get root_passwd_hash; then
  PASS_HASH="$(VBoxControl --nologo guestproperty get root_passwd_hash | cut -d' ' -f 2)"
  usermod -p "$PASS_HASH" root
fi
