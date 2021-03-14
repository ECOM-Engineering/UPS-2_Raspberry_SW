"""
This is the interface to the UPS-2 power supply

Place a call to this service in /etc/rc.local:
python3 /path/to/ups2_serial.py &
"""

import serial
import time
import sys
import os
import fcntl

def ecReadline(ser):
    """Returns a string from serial line until a <CR> chahacter."""
    rxLine = ""
    charCount = 0
    while True:
        rxChar = ser.read(1)
        if (rxChar == b"\n"):
            charcount = 0
            return rxLine
        else:
            if (rxChar != b"\r"): #ignore \r EOL characer
                charCount +=1
                rxLine +=rxChar.decode("ascii")



def ecExecSerCommand(rxLine):
    """Check if commands come from UPS and execute."""
    command = "--"
     #linux system commands from UPS
    if rxLine[0:2] == "u!":  #prefix 
        command = rxLine[2:]
        command = "sudo " + command
        #acknowledge before executing shutdown
        ackString = ">OK " + command + "\n"
        ser.write(str(ackString).encode())
        time.sleep(1) #give UPS a chance to read the ack String
 #       ser.send_break(1000.0) 
        os.system(str(command).encode()) #this will normally execute a shutdown command
        
    else:
        if rxLine[0:2] == "u?": 
            command = rxLine[2:]
            if(command == "ready"): #watchdog
                ackString = ">OK " + command + "\n"
                ser.write(str(ackString).encode())
 
    print("Command = " + command)
    return ""

        
#        os.system(command)

if __name__ == "__main__":
    #ser = serial.Serial('/dev/serial0', 38400, timeout = 1) # ttyACM1 for Arduino board
    """ This service handles serial communication with ECOM UPS-2 power supply. """
    ser = serial.Serial(
    port='/dev/serial0',
    baudrate = 38400,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=30)

    if ser.isOpen(): ser.close()
    ser.open()
    #let the Tx line stabilize
    #time.sleep(1)
    localtime = time.asctime( time.localtime(time.time()) )
    
    testCommand = ">Hi! " + localtime + "\n" 
    print (testCommand)
    ser.write(str(testCommand).encode())
 
#    ser.write(str("\r\nsending break ... ").encode())
#    ser.send_break(100.0) #400ms
#    ser.write(str("break sent\r\n").encode())
#    print("\n\rbreak sent")
    rxLine = ""
    charCount = 0
    while True:
        try:
            #lock serial interface in order to prevent interfering by other tasks
            fcntl.flock(ser, fcntl.LOCK_EX)
            rxLine = ecReadline(ser)
#            fcntl.flock(ser, fcntl.LOCK_UN)
            rxLine = ecExecSerCommand(rxLine)
            #unlock interface after processing rx data
            fcntl.flock(ser, fcntl.LOCK_UN)
            time.sleep(1.5) ##allow serial port by other process 
            rxLine +=rxChar.decode("ascii")
        except:
            pass
    print ("Restart")
    #following code should never be executed
    ser.flush() #clean up
    ser.close()


#if __name__ == "__main__":
#    import sys
#    main()

    
