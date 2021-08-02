#!/usr/bin/env python3

# MIT License see https://opensource.org/licenses/MIT
# copyright (c) 2021 Klaus Mezger, ECOM Engineering

''' This script is part of the UPS2 system, used in parallel mode.

The script monitors input port BCM20, that is set by UPS2 hardware.
Signals at this ports are similar to key actions and are simulated by the external UPS2 hardware.
The input is low active and will be monitored for active and pause times.

For autostart, call this script from file /etc/rc.local
    /home/pi/Projects/UPS2/python3 ups2_portHandler.py
    
IMPORTANT: Activate pullup on input port in file /boot/config.txt
    gpio=20=ip,pu

'''

import gpiod  #install this with 'sudo apt install python3-libgpiod'
import time
import sys
import os

chip = gpiod.Chip("0")
inPort = chip.get_line(20)
inPort.request("UPS-2", type=gpiod.LINE_REQ_EV_BOTH_EDGES)

outPort = chip.get_line(21)
outPort.request("UPS-2", type=gpiod.LINE_REQ_DIR_OUT)

outPort.set_value(1)

print("ready")
t_keyrelease = time.time()
pauseTime = 999 #prevent false trigger of double click

while True:
    try:
        keyAction = "NO_KEY"
        #wait for key pressed
        event = inPort.event_read() #falling edge: key pressed
        print(event)
        print("type", event.type)
        print('timestamp: {}.{}'.format(event.sec, event.nsec))
        if (event.type == 1):
            print("first event should be falling --> ignore")
            continue #retry wait for falling edge
        counter = 1
        t_keypress = event.sec + (event.nsec * 10e-10)
        pauseTime = t_keypress - t_keyrelease 
        
        #wait for key released
        event = inPort.event_read() #rising edge: key released
        print("type", event.type)
        print('timestamp: {}.{}'.format(event.sec, event.nsec))
        t_keyrelease = event.sec + (event.nsec * 10e-10)
        pulseTime = t_keyrelease - t_keypress

        #analyze command
        if pulseTime < 0.5:
            if pauseTime < 0.5: #this is a double click, system restarts
                keyAction = "DOUBLE_PRESS"
                os.system("sudo shutdown -r now")
#            else:
#                keyAction = "SHORT_PRESS" #not used here, handled by UPS2 HW
        elif pulseTime > 5:  #system shuts down, UPS2 HW powers raspi off
            keyAction = "SUPER_LONG_PRESS"
            os.system("sudo shutdown -h now")
 
        elif pulseTime > 2:
            keyAction = "LONG_PRESS"
            os.system("sudo shutdown -h now")

        print("keyAction =", keyAction)             
                
    except KeyboardInterrupt:
        chip.close()
        break
print("ciao")
