import ups2_Interface as test
import sys
import os
import time


ser = test.ecInitSerial('/dev/serial0')
ret = test.ecReqBootloader(ser)
print(ret)
time.sleep(2)

command = 'sudo pkill -f ups2_serial.py'
os.system(str(command).encode())
ser.close()

command = 'stm32flash -w UPS-2_G030.bin -v -g 0x0 /dev/serial0'
os.system(str(command).encode())

command = 'python3 ups2_serial.py &'
os.system(str(command).encode())


