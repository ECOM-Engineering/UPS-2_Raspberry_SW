"""Module containimg functions for serial communication with UPS-2 power supply.

Module ups2_serial.py must be active in background.
"""

import serial
import fcntl

def ecInitSerial(device = '/dev/serial0'):
    '''Opens serial device and returns a handle'''


    ser = serial.Serial(
    port= device,
    baudrate = 38400,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=3)

    if ser.isOpen(): ser.close()
    ser.open()
    return ser

def ecReadline(ser):
    """Returns a string from serial line until a <CR> character."""
    rxLine = ""
    charCount = 0
    while True:
        rxChar = ser.read(1)
        if (rxChar == b"\n"): #end of string
            charcount = 0
            return rxLine
        else:
            if (rxChar != b"\r"): #ignore \r EOL characer
                charCount +=1
                rxLine +=rxChar.decode("ascii")

def ecFormatAnalog(analogStr):
    '''Add units to analogStr 'main,batt,temp' and return as a list.'''

    units = ('V ','V ','°C')
    l = []
    v = analogStr.split(',')
    for i in range(3):
        l.append(v[i] + units[i])
    return l                 

def ecGetUPSValues(ser):
    '''Requests values from UPS-2'''
    try:
        request = "r?status\n"
        fcntl.flock(ser, fcntl.LOCK_EX)
        ser.write(str(request).encode())
        status = ecReadline(ser) #UPS returns hex coded power status
        #        print(status)
        request = "r?analog\n"
        ser.write(str(request).encode())
        analog = ecReadline(ser)
        analog = analog[2:]
        fcntl.flock(ser, fcntl.LOCK_UN)
        #decompose status message
        statusHex =""
        statusHex = status[2:8] #extract hex status
        ups2Version = status[10:]
#        return {'statusHex' : statusHex, 'analog': analog, 'ups2Ver': ups2Version}    
        return(statusHex, analog, ups2Version)
    except:
        print("exception happended @ ecGetUPSValues()")
        pass

def ecReqUPSPowerDown(ser):
    '''Initiates a Pi shutdown and executes power off after Pi is down'''
    
    ack =''
    try:
        request = "r?shutdown -P\n"
        fcntl.flock(ser, fcntl.LOCK_EX)
        ser.write(str(request).encode())
        ack = ecReadline(ser)
        print('Response UPS = ', ack)
        fcntl.flock(ser, fcntl.LOCK_UN)
        return(ack)
    except:
        print("exception happended @ ecReqUPSPowerDown()")
    pass   
