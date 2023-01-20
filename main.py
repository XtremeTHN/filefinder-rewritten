import os, sys, argparse, time
from modules.funcs import jsonEx

yes_no = ['S','N']
keys = []
data = jsonEx.get('modules/exts.json')
for x in data:
    keys.append(x)

parser = argparse.ArgumentParser('Finder v0.0    Buscador de archivos, uso abajo')
parser.add_argument('-tui', '--terminal-user-interface', '--terminal-ui', action='store_true', dest='tui', help='Muestra una interfaz de usuario en la terminal')
parser.add_argument('-f', '--find', action='store', choices=keys, metavar="TYPE_OF_EXT_TO_BROWSE", dest='ext_choice', help='Especifica un tipo de extension para buscar, por ejemplo, "audio" o "images"')
parser.add_argument('-p', '--path', action='store', dest='path', help="Se usa con el argumento --find, especifica la carpeta en donde buscar")
parser.add_argument('-ud', '--upload-drive', action='store_true', dest='drive', help="Sube archivos encontrados a google drive")
parser.add_argument('-ec','--edit-config', action='store_true', dest='upd_choice', help="Edita la configuracion")
parser.add_argument('-u','--update',action='store_true', dest='update', help="Actualiza el script")

obj = parser.parse_args()

if obj.tui:
    from modules.funcs import termui, finder, printc
    from pystyle import Colors, Colorate
    from datetime import datetime
    key_capitalized = []
    for x in keys:
        key_capitalized.append(x.capitalize())
    print(Colorate.Horizontal(Colors.red_to_blue,"[INFO]"), f"Que quieres buscar hoy?     Hora actual: {datetime.now().time().replace(microsecond=0, second=0)}")
    choice = termui.terminal(key_capitalized)
    printc("Donde empiezo a buscar?: ", Colors.red_to_blue, endx='')
    browse_path = input()
    if not os.path.exists(browse_path):
        printc("Carpeta no existente", Colors.red)
        sys.exit(1)
    if not os.path.isdir(browse_path):
        printc("El directorio que se proporciono no es una carpeta", Colors.red)
        sys.exit(2)
    if choice != None:
        find_obj = finder(browse_path,keys[choice])
        result = find_obj.find()
        if type(result) == int:
            printc("No se encontro ningun archivo con las extensiones predeterminadas", Colors.red)
            printc("Deseas sugerir otra extension? (S/N): ", Colors.red_to_blue)
            choice = termui.terminal(yes_no)
            if yes_no[choice] == 'S':
                ext = input("Ingresa la extension con la que quieres buscar: ")
                if ext[0:1] == ".":
                    ext = ext[1:len(ext)]
                result = find_obj.find_userext(ext)
                if type(result) == int:
                    print("No se encontro ningun archivo")
                else:
                    printc("Deseas guardar la extension en la configuracion?", Colors.red_to_blue)
                    choice = termui.terminal(yes_no)
                    if yes_no[choice] == 'S':
                        data['user'].append(ext)
                        jsonEx.update_json('modules/exts.json',data)
        printc("Esto fue lo que encontre: ", Colors.red_to_blue)
        for x in result:
            if len(result[x]) > 1:
                print(Colorate.Horizontal(Colors.blue_to_red,'Extension:'),x,Colorate.Horizontal(Colors.green_to_blue,'Archivos:'),result[x])
            else:
                print(Colorate.Horizontal(Colors.blue_to_red,'Extension:'),x,Colorate.Horizontal(Colors.green_to_blue,'Archivo:'),result[x])
        #time.sleep(3)
        printc("Deseas buscar un archivo en especifico en los archivos ya buscados?", Colors.red_to_blue)
        choice = termui.terminal(yes_no)
        if yes_no[choice] == 'S':
            file = input("Escribe el nombre del archivo (No tienes que ser tan especifico): ")
            finded_file = find_obj.find_in_list(file,strict=True)
            if len(finded_file) < 1:
                printc("No hubo coincidencias", Colors.dark_red)
            else:
                printc("Coincidencias:",Colors.red_to_blue)
                print(finded_file)
    else:
        printc("Esc presionado, saliendo...",Colors.red_to_blue)
        sys.exit()