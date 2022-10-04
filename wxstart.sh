#!/bin/bash

# This uses a controlbyweb webrelay device at .224 to cycle power on the weather radio and
# start the program in a screen.
# Sometimes the serial converter gets confused and you need to re-do this.

curl -s "http://192.168.1.224/state.xml?relayState=2" >> /mnt/somedir/logfile.txt
/usr/bin/screen -S weather -d -m sudo /usr/bin/python /home/scripts/wxs250.py

exit
