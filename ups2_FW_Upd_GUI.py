import PySimpleGUI as sg
import ups2_update

''' Select binary firmware file and update via bootloader. '''

def GetFileDialog():
    success = False
    sg.SetOptions(auto_size_buttons=True, font='Helvetica 11')

    layout = [[sg.Text('Select Firmware Version')],
              [sg.Text('File', size=(15, 1)), sg.InputText(key='_file_'),
                  sg.FileBrowse(button_text = '...' , initial_folder = './', file_types=(("UPS-2 Firmware", "*.bin"),))],
              [sg.Button('Update', key = '_btn_upd_', disabled = True), sg.Button('Cancel')]]

    window = sg.Window('Select UPS-2 Firmware Update',layout)
    while True:
        event, values = window.Read(timeout=200)
        if(values['_file_'] != ''):
            window['_btn_upd_'].update(disabled = False)
 
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

if __name__ == "__main__":
    newFile = GetFileDialog()
    print(newFile)



    