# -*- coding: utf-8 -*-
"""
Graphical interface for UPS-2 UART serial mode.

Usage:
    * For autostart: put this script in /etc/xdg/lxsession/LXDE-pi/autostart
    * This script needs PySimpleGUI.py found on https://github.com/PySimpleGUI/PySimpleGUI
    * Raspberry serial interface must be enabled (with raspi-config) i.e.
    * ups2_serial.py worker service must be started (instructions see docstring)
"""
#Todo: abs
#    calendar timed functions
#    email and/or other messaging functions

import PySimpleGUI as sg
import os
import ups2_Interface as ups

GUI_Version = 'UPS GUI V0.8 '


print('PySimpleGUI Version', sg.version)

sg.theme('lightGreen')
sg.SetOptions(button_element_size=(9,1), auto_size_buttons=False, font='Helvetica 11')
ser = ups.ecInitSerial()
fT = open("/sys/class/thermal/thermal_zone0/temp", "r") #Pi processor temperature

#globals
bgOFF = 'lightgrey'
bgOK =  '#A2C477'
bgLOW = 'lightblue'
bgHIGH = 'orange'

keyMain = 'K_MAIN_V'
keyBatt = 'K_BATT_V'
keyUSB = 'K_USB'
keyCPU = 'K_CPU_T'
keyPiCPU = 'K_PI_T'

def ecPopWin(count, title = 'ECOM UPS2'):
    '''Opens a modal popup for count seconds and returns "shutdown" or "cancel"

    Args:
        param count: countdown time in seconds    
        param title: String to display in popup banner
    
    '''

    devider = count * 10
    layout2 = [[sg.Text('Pi shuddown in'),
               sg.Text('', key='barValue', size=(3,1), pad=(0,0)), sg.Text('seconds', pad=(0,0))],
              [sg.ProgressBar(devider, orientation='h', size=(20, 20), key='progressbar',
                bar_color=['lightgreen','grey'])],
              [sg.Button('Cancel'), sg.Button('Shutdown NOW', size=(12,1), focus=True)]]
    popWin = sg.Window(title , layout2)

    while True:
        ev2, values2 = popWin.read(timeout=100)
        devider -=1
        if devider:
            popWin['progressbar'].UpdateBar((devider))
            popWin['barValue'].update(devider/10)
            #        popWin.set_title('123')
            if (ev2 == sg.WIN_CLOSED or ev2 == 'Cancel'):
                print('CANCELLED')
                action = 'cancel'
                popWin.close()
                return action    
            elif ev2 == 'Shutdown NOW' or devider < 2:
                print('SHUTTING DOWN')
                action = 'shutdown'
                popWin.close()
                return action    
        


def ecFormatDisplay(sysStatus, window):
    '''Set display attributes according to system state.
    
    This function refreshes the display depending on the system state
    Must be periodically called by the main control loop 

    Args:
        sysStatus:  string received from UPS-2 hardware
        window:     initialized main window 
    '''
    
    s = int(sysStatus, 16) #sysStatus comes as string

    #default values. In dictionary in order to easily update depending on status  
    mainState = dict(key = keyMain,  bgColor = bgOFF, borderW = 1, stat = 'OFF', selected = '')
    battState = dict(key = keyBatt,  bgColor = bgOFF, borderW = 1, stat = 'OFF', selected = '')
    usbState =  dict(key = keyUSB,   text = '---', bgColor = bgOFF, borderW = 1, stat = 'OK', selected = '')
 #   cpuState =  dict(key = keyCPU,   bgColor = bgOFF, borderW = 1, stat = 'OFF', selected = '')
 #   piState =   dict(key = keyPiCPU, bgColor = bgOFF, borderW = 1, stat = 'OFF', selected = '')

    #decode status message from UPS
    if s & 0x0001:    #main active
        mainState.update(selected = '@', bgColor = bgOK, borderW = 2)
    elif s & 0x0002:  #batt active
        battState.update(selected = '@', bgColor = bgOK, borderW = 2)
    elif s & 0x0004:  #usb active   
        usbState.update(selected = '@',  text = 'active', bgColor = bgOK, borderW = 2)
    if s & 0x0010:    #main V present
        mainState.update(bgColor = bgOK, stat = 'OK')
    if s & 0x0020:    #batt V present
        battState.update(bgColor = bgOK, stat = 'OK')
    if s & 0x0040:    #usb V present
        usbState.update(bgColor = bgOK, text = 'active')     
    if (s & 0x0110) == 0x0110:    #main V LOW
        mainState.update(stat = 'LOW',   bgColor = bgLOW)
    if s & 0x0200:    #main V HIGH
        mainState.update(stat = 'HIGH',  bgColor = bgHIGH)
    if (s & 0x0420) == 0x0420:    #batt V LOW
        battState.update(stat = 'LOW',   bgColor = bgLOW)
    if s & 0x0800:    #batt V HIGH
        battState.update(stat = 'HIGH',  bgColor = bgHIGH)
    if s & 0x1000:    #CPU temp HIGH
        battState.update(stat = 'HIGH',  bgColor = bgHIGH)
    
    #adapt value displays        
    window['K_MAIN_V'].update(background_color = mainState['bgColor'])
    window['K_MAIN_V'].Widget.configure(borderwidth = mainState['borderW']) #use underlying element
    window['K_MAIN_STATE'].update(mainState['stat'])
    window['K_BATT_V'].update(background_color = battState['bgColor'])
    window['K_BATT_V'].Widget.configure(borderwidth = battState['borderW']) #use underlying element
    window['K_BATT_STATE'].update(battState['stat'])
    window['K_USB'].update(background_color = usbState['bgColor'])
    window['K_USB'].update(usbState['text'])
    #adapt power button

    if s & 0x0004:
 #      window['Power OFF'].set_tooltip('Disabled, if USB 5V supplied')
       window['Power OFF'].update(disabled=True, disabled_button_color=('lightgrey', 'none'))
 
    else:
        window['Power OFF'].update(disabled=False)
 #       window['Power OFF'].SetTooltip('')

# Main window column layout
col1 = [[sg.Text(text='Main supply', key="K_MAIN_LBL", size=(10,0), justification='right')],
       [sg.Text(text='Batt supply', key='K_BATT_LBL', size=(10,1), justification='right')],
       [sg.Text(text='Pi USB', key='K_USB_LBL', size=(10,1),justification='right')]]

col2 = [[sg.Text(text='12.2V', key="K_MAIN_V", relief=sg.RELIEF_SOLID, border_width=1, justification='right', background_color='#A2C477',size=(6,1))],
       [sg.Text(text='5.1V', key="K_BATT_V", relief=sg.RELIEF_SOLID, border_width=1, justification='right', background_color='#A2C477',size=(6,1))],
       [sg.Text(text=' ', key="K_USB", relief=sg.RELIEF_SOLID, justification='center', background_color='lightgrey', size=(6,1))]]

col3 = [[sg.Text('OK', key='K_MAIN_STATE', size=(6,1))],
       [sg.Text('LOW', key='K_BATT_STATE', size=(6,1))],
       [sg.Text('')]]

col4 = [[sg.Text('PS CPU Temp', size=(12,1), justification='right')],
        [sg.Text('Pi CPU Temp', size=(12,1), justification='right')]]

col5 = [[sg.Text(text=' °C', key='K_CPU_T',relief=sg.RELIEF_SOLID, justification='right', background_color='#A2C477',size=(5,1))],
       [sg.Text(text='  °C', key='K_PI_T',relief=sg.RELIEF_SOLID, justification='right', background_color='#A2C477',size=(5,1))]]

#frame layout around readouts
mainFrame = [[ sg.Column(col1), sg.Column(col2), sg.Column(col3), sg.Column(col4), sg.Column(col5)]]

#buttons to appear in frame below
keypanel = [[sg.Button('Power OFF', tooltip='Disabled if USB powered'), sg.Button('Restart'), sg.Button('Standby'), sg.Button('Quit')]]

#frame layout around buttons
layout = [[sg.Frame('Power Supply Overview', mainFrame)],
         [sg.Frame('', keypanel)]]


  
# Display, get values
#window = sg.Window('ECOM UPS GUI V0.8', layout, location=(350,350))
ups2Values = ups.ecGetUPSValues(ser)
ups2Version = ups.ecGetUPSVersion(ser)
print('UPS Status', ups2Values)
analogStr = ups.ecFormatAnalog(ups2Values[1])        

window = sg.Window(GUI_Version + " | " + ups2Version, layout)


piTemp = '0'
counter = 1
divider = 0
while 1:
    event, values = window.read(timeout=10) #time.sleep() may be used instead
    if event in (None, 'Quit'):
        break
    if event == 'Power OFF':
        if ecPopWin(5, 'POWER OFF') != 'cancel':
            ups.ecReqUPSPowerDown(ser)
            os.system('sudo shutdown -P now\n')
    elif event == 'Restart':
        if ecPopWin(5, 'Restart') != 'cancel':
            os.system('sudo shutdown -r now\n')
    elif event == 'Standby':
        if ecPopWin(5, 'Standby') != 'cancel':
            os.system('sudo shutdown now\n')
    if divider < 100: #main processing tick = 1s
        divider +=1
    else:
        divider = 0
        counter  += 1
        #real time value updates
        ups2Values = ups.ecGetUPSValues(ser)
        sysStatus = ups2Values[0]
        print (sysStatus)
        AnalogList = ups.ecFormatAnalog(ups2Values[1])     
        piTemp = fT.readline() 
        fT.seek(0) #reset to first line
        piTemp = piTemp[0:2] + '°C'
        #set display attributes
        ecFormatDisplay(sysStatus, window)  
        #update values
        window['K_MAIN_V'].update(AnalogList[0])
        window['K_BATT_V'].update(AnalogList[1])
        window['K_CPU_T'].update(AnalogList[2])
        window['K_PI_T'].update(piTemp)        

#    time.sleep(.5)
fT.close()
ser.close()
window.close()          
