if [ "$1" != "after" ]
then
	sudo sed 's/GRUB_CMDLINE_LINUX=""/GRUB_CMDLINE_LINUX="net.ifnames=0 biosdevname=0"/' /etc/default/grub | sudo tee /etc/default/grub
	sudo grub-mkconfig -o /boot/grub/grub.cfg
	sudo echo "@reboot `pwd`/rename-interface.sh after">/var/spool/cron/crontabs/root
else
	echo 123>/tmp/new
fi
