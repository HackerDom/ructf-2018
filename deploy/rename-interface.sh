sudo sed 's/GRUB_CMDLINE_LINUX=""/GRUB_CMDLINE_LINUX="net.ifnames=0 biosdevname=0"/' /etc/default/grub | sudo tee /etc/default/grub
sudo grub-mkconfig -o /boot/grub/grub.cfg

