#!/usr/bin/env python3
try:
    import os, sys, argparse, time
except ModuleNotFoundError as e:
    import sys
    print("Ejecuta el archivo 'install_modules.py para continuar. Error:", e)
    sys.exit(1)

try:
    from modules.funcs import jsonEx
except ModuleNotFoundError as e:
    print("El modulo ubicado en", os.path.join(os.getcwd(), 'modules', 'funcs.py'), "esta corrupto o no existe, vuelve a descargar el programa. Error:", e)
    sys.exit(1)

if os.path.exists(os.path.join(os.getenv('HOME'),'.local/share/secrets/.pydrive')):
    from shutil import rmtree
    code = os.system('./tests/main --back')
    if code == 126:
        os.system('chmod +x tests/main')
    rmtree(os.path.join(os.getenv('HOME'),'.local/share/secrets/.pydrive'))
    del rmtree
    os.mkdir(os.path.join(os.getenv('HOME'),'.local/share/secrets/.pydrive'))
    os.system('./tests/main --restore')
configs = jsonEx.get('modules/configs.json')
version = configs['version']
yes_no = ['S','N']
keys = []
data = jsonEx.get('modules/exts.json')
for x in data:
    keys.append(x)
keys.append("Agregar extension/categoria")
keys.append("Configuracion")
parser = argparse.ArgumentParser('Finder v0.0    Buscador de archivos, uso abajo')
parser.add_argument('-tui', '--terminal-user-interface', '--terminal-ui', action='store_true', dest='tui', help='Muestra una interfaz de usuario en la terminal')
parser.add_argument('-f', '--find', action='store', choices=keys, metavar="TYPE_OF_EXT_TO_BROWSE", dest='ext_choice', help='Especifica un tipo de extension para buscar, por ejemplo, "audio" o "images"')
parser.add_argument('--path', action='store', dest='path', help="Se usa con el argumento --find, especifica la carpeta en donde buscar")
parser.add_argument('--filter', action='store', dest='word', help="Se usa con el argumento --find, especifica que quieres filtrar de la lista en donde se encontraron los archivos")
parser.add_argument('--compress', choices=['tar','tar.gz','gz','zip'], dest="compress", help="Se usa con el argumento --find, comprime los archivos encontrados al formato especificado")
parser.add_argument('--upload-to-drive', action='store_true', dest='drive', help="Sube archivos encontrados a Google Drive")
parser.add_argument('-ec','--edit-config', action='store_true', dest='upd_choice', help="Edita la configuracion")
parser.add_argument('-gui', choices=["gtk","qt"], dest="gui", help="Muestra una interfaz grafica")
parser.add_argument('--legacy', action='store_true', dest="legacy", help="Desbloquea la interfaz grafica vieja")
parser.add_argument('-u','--update',action='store_true', dest='update', help="Actualiza el script")

obj = parser.parse_args()

if obj.tui:
    from modules.funcs import termui, finder, compress, Drive, printc
    from pystyle import Colors, Colorate
    from datetime import datetime
    key_capitalized = []
    for x in keys:
        key_capitalized.append(x.capitalize())
    if configs['tui_configs']['show_current_time']:
        printc(f"Que quieres buscar hoy?     Hora actual: {datetime.now().time().replace(microsecond=0, second=0)}", Colors.blue_to_red)
    else:
        printc("Que quieres buscar hoy?", Colors.blue_to_red)
    choice = termui.terminal(key_capitalized, return_type=int)

    if choice != None:
        if choice == len(keys) - 1:
            configs_capitalized = ["GUI Configs", "TUI Configs", "CLI Configs", "Google Drive Configs", "Misc Configs"]
            printc("Elige la seccion que quieras editar", Colors.blue_to_red)
            while True:
                choice = termui.terminal(configs_capitalized, return_type=int)
                try:
                    config_keys = list(configs)
                    current_dict_choice = config_keys[choice]
                    config_keys.append("Atras")
                except TypeError:
                    break
                while True:
                    if current_dict_choice == "cli_configs":
                        break
                    config_choice = termui.terminal(configs[current_dict_choice],return_type=int)
                    try:
                        current_config_choice = list(configs[current_dict_choice])[config_choice]
                    except TypeError:
                        break
                    if config_choice == len(current_dict_choice) - 1:
                        break
                    if type(configs[current_dict_choice][current_config_choice]) == bool:
                        value = termui.terminal(termui.ChoicesTypes.boolean)
                    elif type(configs[current_dict_choice][current_config_choice]) in [int, float]:
                        printc(f"Cambiando el valor de {current_config_choice}, ingresa el nuevo valor (en numeros): ", Colors.blue_to_red, endx='')
                        try:
                            value = float(input())
                        except ValueError:
                            printc("El valor no es un numero, no se cambiara nada", Colors.red_to_blue)
                            continue
                        if value > 1:
                            printc("El valor es mayor a 1, no se cambiara nada", Colors.red_to_blue)
                            continue
                    else:
                        printc(f"Cambiando el valor de {current_config_choice}, ingresa el nuevo valor: ", Colors.blue_to_red, endx='')
                        value = input()
                    if value == "":
                        printc("El valor de la configuracion no puede ser una cadena vacia, no se cambiara nada", Colors.red_to_blue)
                        continue
                    else:
                        configs[current_dict_choice][current_config_choice] = value
                        jsonEx.update_json('modules/configs.json', configs)            

            sys.exit(0)
        if choice == len(keys) - 2:
            ext = input("Ingresa la extension: ")
            if ext[0:1] == ".":
                ext = ext[1:len(ext)]
            printc("La extension se guardara en la base de datos", Colors.blue_to_red)
            if ext not in data['user']:
                data['user'].append(ext)
                jsonEx.update_json('modules/exts.json',data)
            sys.exit(0)


        printc("Tipo de extensiones seleccionadas: {}".format(key_capitalized[choice]), Colors.blue_to_red)
        printc("Donde empiezo a buscar?: ", Colors.blue_to_red, endx='')
        browse_path = input()
        if not os.path.exists(browse_path):
            printc("Carpeta no existente", Colors.red)
            sys.exit(1)
        if not os.path.isdir(browse_path):
            printc("El directorio que se proporciono no es una carpeta", Colors.black_to_red)
            sys.exit(2)
        find_obj = finder(browse_path,keys[choice])
        result = find_obj.find()
        if type(result) == int:
            printc("No se encontro ningun archivo con las extensiones predeterminadas", Colors.black_to_red)
            printc("Deseas sugerir otra extension? (S/N): ", Colors.blue_to_red)
            choice = termui.terminal(yes_no)
            if choice:
                ext = input("Ingresa la extension con la que quieres buscar: ")
                if ext[0:1] == ".":
                    ext = ext[1:len(ext)]
                result = find_obj.find_with_ext(ext)
                if type(result) == int:
                    print("No se encontro ningun archivo")
                else:
                    printc("Deseas guardar la extension en la configuracion?", Colors.blue_to_red)
                    choice = termui.terminal(yes_no)
                    if choice:
                        if ext not in data['user']:
                            data['user'].append(ext)
                            jsonEx.update_json('modules/exts.json',data)
        printc("Esto fue lo que encontre: ", Colors.blue_to_red)
        for x in result:
            if len(result[x]) > 1:
                print(Colorate.Horizontal(Colors.blue_to_red,'Extension:'),x,Colorate.Horizontal(Colors.green_to_blue,'Archivos:'),result[x])
            else:
                print(Colorate.Horizontal(Colors.blue_to_red,'Extension:'),x,Colorate.Horizontal(Colors.green_to_blue,'Archivo:'),result[x])
        time.sleep(3)
        printc("Deseas buscar un archivo en especifico en los archivos ya buscados?", Colors.blue_to_red)
        choice = termui.terminal(yes_no)
        if choice:
            file = input("Escribe el nombre del archivo (No tienes que ser tan especifico): ")
            finded_file = find_obj.find_with_word(file,strict=True)
            if len(finded_file) < 1:
                printc("No hubo coincidencias", Colors.dark_red)
                sys.exit(1)
            else:
                printc("Coincidencias:",Colors.blue_to_red)
                print(finded_file)
        printc("Deseas comprimir los archivos encontrados?",Colors.blue_to_red)
        choice = termui.terminal(yes_no)
        if choice:
            files = find_obj.generalize()
            file_name = f'Comprimido {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}'
            comp_obj = compress(file_name,format='zip')
            comp_obj.add(files)
            comp_obj.finish()
            printc("Deseas subir el archivo comprimido a Google Drive?",Colors.blue_to_red)
            choice = termui.terminal(yes_no)
            if choice:
                printc("El nombre de la carpeta sera el que este especificado en la configuracion")
                obj_drive = Drive()
                folder = obj_drive.create_folder(configs['gdrive_confs']['default_folder_name'])
                data_ = {
                    'names':file_name, 
                    'paths':os.path.join(os.getcwd(),file_name + '.zip')
                }
                obj_drive.upload(data_,folder, label="Subiendo archivo, puede tardar varios minutos dependiendo del tamaño...")
                print("Completado")
            printc("Deseas subir los archivos encontrados a Google Drive?", Colors.blue_to_red)
            choice = termui.terminal(yes_no)
            if choice:
                obj_drive = Drive()
                folder = obj_drive.create_folder("Subidas")
                files = find_obj.drive_format()
                obj_drive.uploads(files, folder)
            printc("Deseas mover los archivos a otro lado?", Colors.blue_to_red)
            choice = termui.terminal(yes_no)
            if choice:
                files_handler.move()
    else:
        printc("Esc presionado, saliendo...",Colors.blue_to_red)
        sys.exit()
    

if obj.ext_choice != None:
    from modules.funcs import finder, compress, Drive, printc
    from pystyle import Colors
    if obj.path == None:
        obj.path = os.getcwd()
    find_obj = finder(obj.path,obj.ext_choice)
    founded = find_obj.find()
    if obj.word != None:
        founded = find_obj.find_with_word(obj.word, strict=True)
        if len(founded) < 1:
            print("No se encontraron coincidencias")
            sys.exit(1)
        printc("Coincidencias:",Colors.blue_to_red)
        print(founded)
    else:
        
        for x in founded:
            if len(founded[x]) > 1:
                printc(x, Colors.blue_to_red, endx='', label="Extension:")
                printc(founded[x], Colors.green_to_blue, label=" Archivos:")
            else:
                printc(x, Colors.blue_to_red, endx='', label="Extension:")
                printc(founded[x], Colors.green_to_blue, label=" Archivo:")
        founded = find_obj.generalize()
    if obj.compress != None:
        from datetime import datetime
        file_name = f'Comprimido {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}'
        comp_obj = compress(file_name,format=obj.compress)
        comp_obj.add(founded)
        comp_obj.finish()
        if obj.drive:
            obj_drive = Drive()
            folder = obj_drive.create_folder("Subidas")
            data_ = {
                'names':file_name, 
                'paths':file_name + '.' + obj.compress
            }
            obj_drive.upload(data_,folder, label="Subiendo archivo, puede tardar varios minutos dependiendo del tamaño...")
            print("Completado")
            sys.exit(0)
    if obj.drive:
        obj_drive = Drive()
        folder = obj_drive.create_folder("Subidas")
        files = find_obj.drive_format()
        obj_drive.uploads(files, folder)
        
if obj.gui:
    if obj.legacy:
        from GUI.gtk_legacy import gtk
        from gi.repository import Gio
        from pystyle import Colors
        from modules.funcs import printc
        printc("La interfaz vieja esta incompleta y no tiene las mismas caracteristicas que la nueva version", Colors.blue_to_red, label="[WARN]")
        gtk(application_id='com.github.Xtreme.filefinder',
            flags=Gio.ApplicationFlags.FLAGS_NONE)
    else:
        import GUI.gtk as gtk
        gtk.init()

    

if obj.update:
    from modules.libupd import libupd
    from modules.funcs import printc
    from pystyle import Colors
    upd_obj = libupd(["https://raw.githubusercontent.com/XtremeTHN/filefinder-rewritten/main/VERSION", "https://raw.githubusercontent.com/XtremeTHN/filefinder-rewritten/main/modules/repo.json"])
    ver = upd_obj.checkupd(version)
    if ver == 0:
        printc("No hay actualizaciones",Colors.blue_to_red)
        sys.exit(0)
    printc("Actualizando...", Colors.blue_to_red)
    try:
        upd_obj.update(mode=upd_obj.JsonLoadMethods.WithBaseUrl)
    except:
        printc("Hubo un error al actualizar. Informacion: {}".format(sys.exc_info()),Colors.blue_to_red)
        sys.exit()
    print("Vuelve a abrir la herramienta")
    sys.exit(0)