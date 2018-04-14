#!/bin/bash

/usr/bin/Xorg &

sleep 5

export DISPLAY=":0"
/usr/bin/xset s off dpms 0 0 0

/usr/bin/unclutter -idle 1.00 -root &
/root/tcpimg &

wait
