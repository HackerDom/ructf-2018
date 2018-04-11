# sudo rm /etc/apt/sources.list
# sudo cp sources.list /etc/apt/sources.list
sudo apt-get update
sudo apt-get install -y nginx libltdl7 gcc make perl
sudo mount /dev/cdrom /mnt
sudo /mnt/VBoxLinuxAdditions.run
sudo ./cloud-init.sh
sudo ./rename-interface.sh
sudo sed -i 's/enp8s0/eth0/g' /etc/network/interfaces 
# wget https://download.docker.com/linux/ubuntu/dists/xenial/pool/stable/amd64/docker-ce_17.03.2~ce-0~ubuntu-xenial_amd64.deb
# sudo dpkg -i docker-ce_17.03.2~ce-0~ubuntu-xenial_amd64.deb
# sudo cp docker-compose /usr/bin
# sudo python3 deploy_services.py
