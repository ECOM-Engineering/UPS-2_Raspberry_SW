import PySimpleGUI as sg
import ups2_update

def GetFileDialog():
    success = False
    sg.SetOptions(auto_size_buttons=True, font='Helvetica 11')

    form_rows = [[sg.Text('Select Firmware Version')],
                 [sg.Text('File', size=(15, 1)), sg.InputText(key='_file_'),
                  sg.FileBrowse(button_text = '...' , initial_folder = './', file_types=(("UPS-2 Firmware", "*.bin"),))],
                 [sg.Button('Update'), sg.Cancel()]]

    window = sg.Window('Select UPS-2 Firmware Update')
    event, values = window.Layout(form_rows).Read()
    while True:
        if event in (None, 'Cancel'):
             window.close()
             return('')
        elif event == 'Update':
            success = ''
            newFile = values['_file_']
            if(newFile != ''):
                success = ups2_update.ecUpdateUPS(newFile, True)
                window.close()
            return newFile

if __name__ == "__main__":
    newFile = GetFileDialog()
    print(newFile)



    