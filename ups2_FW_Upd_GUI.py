import PySimpleGUI as sg
import ups2_update
import os


''' Select binary firmware file and update via bootloader. '''

def GetUpdDialog(win_location = (50,50)):
    initPath =os.path.dirname(os.path.realpath(__file__)) 

    success = False
    sg.SetOptions(auto_size_buttons=True, font='Helvetica 11')

    layout = [[sg.Text('Select Firmware Version')],
              [sg.Text('File', size=(15, 1)), sg.InputText(key='_file_'),
                  sg.FileBrowse(button_text = '...' , initial_folder = initPath, file_types=(("UPS-2 Firmware", "*.bin"),))],
              [sg.Button('Update', key = '_btn_upd_', disabled = True), sg.Button('Cancel')]]

    window = sg.Window('Select UPS-2 Firmware Update',layout, location = win_location)
    while True:
        event, values = window.Read(timeout=200)
 
        if event in (None, 'Cancel'):
             window.close()
             return('')
        elif event == '_btn_upd_':
            success = ''
            newFile = values['_file_']
            if(newFile != ''):
                success = ups2_update.ecUpdateUPS(newFile, True)
                window.close()
                return newFile

        #enable update button if file selected       
        if(values['_file_'] != ''):
            window['_btn_upd_'].update(disabled = False) 

if __name__ == "__main__":
    newFile = GetUpdDialog()
    print(newFile)



    