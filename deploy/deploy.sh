#!/bin/bash
# sudo rm /etc/apt/sources.list
# sudo cp sources.list /etc/apt/sources.list
sudo apt-get update
sudo apt-get install -y nginx libltdl7 gcc make perl
sudo cp cloud-init.service /lib/systemd/system/
sudo systemctl enable cloud-init
sudo mount /dev/cdrom /mnt
sudo /mnt/VBoxLinuxAdditions.run
sudo ./cloud-init.sh
sudo ./rename-interface.sh
sudo sed -i 's/enp8s0/eth0/g' /etc/network/interfaces
sudo reboot

