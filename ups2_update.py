import ups2_Interface as test
import sys
import os
import time

def ecUpdateUPS(newFile = 'UPS-2_G030.bin', backup = False):
    ser = test.ecInitSerial('/dev/serial0')
    ret = test.ecReqBootloader(ser) #send a request to UPS2
    print(ret)
    time.sleep(2) #todo ack from UPS2 instead of wait

    #we have to free serial interface for flashing software
    command = 'sudo pkill -f ups2_serial.py'
    os.system(str(command).encode())
    ser.close()
    if backup == True:
        command = 'stm32flash -r UPS-2_G030.bak /dev/serial0'
        os.system(str(command).encode())
    command = 'stm32flash -w ' + newFile + ' -v -g 0x0 /dev/serial0'
    ret = os.system(str(command).encode())

    #now restore serial interface
    command = 'python3 ups2_serial.py &'
    ret = os.system(str(command).encode())

    return ret

if __name__ == "__main__":
    ecUpdateUPS()
