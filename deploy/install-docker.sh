#!/bin/bash
wget https://download.docker.com/linux/ubuntu/dists/xenial/pool/stable/amd64/docker-ce_17.12.1~ce-0~ubuntu_amd64.deb
sudo dpkg -i docker-ce_17.12.1~ce-0~ubuntu_amd64.deb
sudo cp docker-compose /usr/bin
