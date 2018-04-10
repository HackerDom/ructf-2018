#!/bin/bash -e

TEAM=${1?Syntax: ./launch_vm.sh <team_id>}

if ! [[ $TEAM =~ ^[0-9]+$ ]]; then
  echo "team number validation error"
  exit 1
fi

vm="test_team${TEAM}"

if ! VBoxManage showvminfo "$vm" &>/dev/null; then
  VBoxManage clonevm "ructf2018" --register --name "$vm" --basefolder="/home/vbox_drives/" --mode all
fi

if ! VBoxManage list runningvms | grep -qP "\W${vm}\W"; then
  VBoxManage modifyvm "$vm" --bridgeadapter1 "eth0"
fi

VBoxManage guestproperty set "$vm" team "${TEAM}"
VBoxManage guestproperty set "$vm" root_passwd_hash "$(cat /home/cloud/root_passwd_hash_team${TEAM}.txt)"

VBoxManage startvm "$vm" --type headless
