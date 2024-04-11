#!/bin/bash
#
# panda auto setup script for mars mode on PiOS
#
# will install requirements, build custom firmware, flash panda, and setup boot script

echo '----------------------------------------------------------------------'
echo ' '
echo '                   ** MarsMode install for PiOS! **'
echo ' '
echo '----------------------------------------------------------------------'

BIND=`dirname $0`

# check for PiOS
echo -n "Checking for approved distro... "
if [ -f '/etc/apt/sources.list.d/raspi.list' ]
then
	echo "OK"
else
	echo "OOPS"
	echo "- This installer has only been tested for use ONLY with PiOS."
	echo -n "- *** Proceed anyway? [y/N] "
	read piosOverride
	if [ "q$piosOverride" == "qy" ]
	then
		echo '- Proceeding with OVERRIDE. Good luck!'
	else
		echo '- Aborted due to unfamiliar territory. Try again with PiOS.'
		exit -1
	fi
fi

# check for root
echo -n "Checking for root access... "
sleep 1 && echo "SKIPPED" && sleep 1

# install dependencies
echo -n "Installing system dependencies... "
sudo apt-get update >/dev/null 2>&1
sudo apt-get install -y dfu-util gcc-arm-none-eabi python3-pip libffi-dev git scons screen >/dev/null 2>&1
sleep 1 && echo "DONE" && sleep 1

# grab the git checkout
echo -n "Checking out spleck panda git repo... "
git clone https://github.com/spleck/panda.git ~/panda >/dev/null 2>&1
python -m venv ~/panda/ >/dev/null 2>&1
export PATH=~/panda/bin:$PATH
cd panda
sleep 1 && echo "DONE" && sleep 1

# install requirements
echo -n "Installed app dependencies... "
pip install -r requirements.txt >/dev/null 2>&1
python setup.py install >/dev/null 2>&1
sleep 1 && echo "DONE" && sleep 1

# check for / setup udev rules
echo -n "Checking udev configuration... "
sudo tee /etc/udev/rules.d/11-panda.rules <<EOF >/dev/null
SUBSYSTEM=="usb", ATTRS{idVendor}=="bbaa", ATTRS{idProduct}=="ddcc", MODE="0666"
SUBSYSTEM=="usb", ATTRS{idVendor}=="bbaa", ATTRS{idProduct}=="ddee", MODE="0666"
SUBSYSTEM=="usb", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="df11", MODE="0666"
EOF
sudo udevadm control --reload-rules && sudo udevadm trigger
sleep 1 && echo "DONE" && sleep 1

# build custom panda firmware
cd board
echo -n "Building firmware... "
scons -u >/dev/null 2>&1
sleep 1 && echo "DONE" && sleep 1

# symlink hotfix for flashing
for dir in ~/panda/lib/python*/site-packages/pandacan*; do ln -s ~/panda/board $dir/board; done

echo -n "Recovery mode panda... "
./recover.py
sleep 1 && echo "DONE" && sleep 1

echo -n "Flashing panda... "
./flash.py
sleep 1 && echo "DONE" && sleep 1

# add rc.local execution if not present
echo -n 'Checking rc.local for startup... '
grep -v ^exit /etc/rc.local >/tmp/.rcl
echo screen -d -m -S mars /home/$USER/panda/examples/marsmode/marsmode-active.sh >>/tmp/.rcl
echo exit 0 >>/tmp/.rcl
cat /tmp/.rcl | sudo tee /etc/rc.local >/dev/null
sleep 1 && echo DONE && sleep 1

# run marsmode-active.sh to link default active script
echo -n 'Setting default MarsMode script to marsmode-mediavolume-basic... '
$BIND/marsmode-active.sh $BIND/marsmode-mediavolume-basic.py >/dev/null
sleep 1 && echo OK && sleep 1

# add boot config to enable single cable for power+data
echo dtoverlay=dwc2,dr_mode=host | sudo tee -a /boot/firmware/config.txt >/dev/null

# done
echo '----------------------------------------------------------------------'
echo ' '
echo '        ** MarsMode install complete. Ready to GO! **'
echo ' '
echo "  To adjust startup script: $BIND/marsmode-active.sh <script>"
echo ' ' && sleep 1
