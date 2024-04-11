
**Raspberry Pi4 + PiOS + White Comma Panda Install**

# Operating System image onto MicroSD Card

Go to [raspberrypi.com](http://raspberrypi.com), click Software and download Raspberry Pi Imager for MacOS, Windows or Ubuntu

Open Imager, Select Pi4, Select Other -> Raspberry PiOS Lite (64-bit), Select your Memory Card and Click Next

OS Customization Settings: hostname, user+password, wireless, and locale

Click Write and Confirm Overwriting All Files on the memory card

When complete, remove memory card, place into pi4, attach white comma panda via usb, and power up the pi.

# Installing the Software

Login via ssh from remote or using keyboard and mouse locally

# Automated install for PiOS:

curl <https://spleck.net/mars-mode-install> | bash

That's it. (Good luck!)

Or if you prefer to do the steps manually (or in case of difficulties):

#  Manual PiOS / Debian / Ubuntu Install Steps

# Install system dependencies

sudo apt-get update

sudo apt-get install -y dfu-util gcc-arm-none-eabi python3-pip libffi-dev git scons screen

# Clone spleck's panda repo for Mars Mode

git clone <https://github.com/spleck/panda.git>

# setup and activate the local python environment

python -m venv ~/panda/

export PATH=~/panda/bin:$PATH

cd ~/panda

# install panda external requirements

pip install -r requirements.txt

# install panda software

python setup.py install

# add device mappings for udev

sudo tee /etc/udev/rules.d/11-panda.rules <<EOF

SUBSYSTEM=="usb", ATTRS{idVendor}=="bbaa", ATTRS{idProduct}=="ddcc", MODE="0666"

SUBSYSTEM=="usb", ATTRS{idVendor}=="bbaa", ATTRS{idProduct}=="ddee", MODE="0666"

SUBSYSTEM=="usb", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="df11", MODE="0666"

EOF

sudo udevadm control --reload-rules && sudo udevadm trigger

# build custom firmware so we can enable write mode

cd board 

scons -u

# add fixup symlink (not sure how else to fix this?)

for dir in ~/panda/lib/python*/site-packages/pandacan*; do ln -s ~/panda/board $dir/board; done

# dfu / recovery if needed

./recover.py

# flash with our firmware

./flash.py

# Launch Mars Mode Panda Agent at Startup

grep -v ^exit /etc/rc.local >/tmp/.rcl

echo screen -d -m -S mars /home/$USER/panda/examples/marsmode/marsmode-active.sh >>/tmp/.rcl

echo exit 0 >>/tmp/.rcl

cat /tmp/.rcl | sudo tee /etc/rc.local

# Add overlay to boot config to allow data on the usb-c power connection from the panda:

echo dtoverlay=dwc2,dr_mode=host | sudo tee -a /boot/firmware/config.txt

# Configure Active Mars Mode Script

cd ~/panda/examples/marsmode

./marsmode-active.sh marsmode-mediavolume-basic.py

# shut down and move to car, ALL DONE!

sudo halt

## Comma.ai and Panda Details

For inforamtion about comma panda visit [comma.ai panda](https://github.com/commaai/panda)

## Licensing

panda software and mars mode scripting are released under the MIT license unless otherwise specified.
