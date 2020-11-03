import argparse        

''' shutdown control using simple switch and LED. '''

def getArgs():
    '''Read arguments from command line'''

    ledDefault = 21
    switchDefault = 20
    powerDefault = ''
 
 
    parser = argparse.ArgumentParser()
                                        
    parser.add_argument("-l","--ledPort", type=int, default=ledDefault, metavar='',
                        help='Enter LED output bcm port default = ' + str(ledDefault))
    parser.add_argument("-s", "--switchPort", type=int, default=switchDefault, metavar='',
                        help='Enter switch control input bcm port default = ' + str(switchDefault))
    parser.add_argument("-p", "--powerPort", type=int, metavar='',
                        help='optional bcm port for ext. power timer')

    args=parser.parse_args()
    worker(args)
#    return args

def worker(ports):
#    ports = getArgs()
    print('LED: GPIO'+str(ports.ledPort),
          'Switch: GPIO'+str(ports.switchPort),
          'Power: GPIO'+str(ports.powerPort))

    chip = gpiod.Chip("0")
    inPort = chip.get_line(ports.switchPort)
    inPort.request("UPS-2", type=gpiod.LINE_REQ_EV_BOTH_EDGES)

    outPort = chip.get_line(ports.ledPort)
    outPort.request("Py_Shutdown", type=gpiod.LINE_REQ_DIR_OUT)
    outPort.set_value(1) #signal raspi is up

    counter = 0
    t_keyrelease = time.time()
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
    #        startTime = time.process_time() 
            t_keyrelease = event.sec + (event.nsec * 10e-10)
            pulseTime = t_keyrelease - t_keypress
    #        print("calc time: ", time.process_time() - startTime)

            counter = counter + 1
            print("counter =", counter,
            "  pulse time= ", pulseTime, "s"
            "  pause time = ", pauseTime)

            #analyze command
            if pulseTime < 0.5:
                if pauseTime < 0.5: #this is a double click
                    keyAction = "DOUBLE_PRESS"
                    os.system("sudo shutdown -r now")
                else:
                    keyAction = "SHORT_PRESS"
            elif pulseTime > 5:
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

if __name__ == "__main__":
    import gpiod
    import time
    import sys
    import os
    getArgs()
