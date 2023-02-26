import json, glob, os, re, sys
from simple_term_menu import TerminalMenu
from pystyle import Colorate
from zipfile import ZipFile
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from statistics import median
from datetime import datetime
from shutil import move as mv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def compress_path(path: list):
    """
        Funcion incompleta
        path: Objeto con un directorio adentro
    """
    media = int(median(range(len(path))))
    for x,v in enumerate(path):
        if x == 0:
            continue
        if x == 1:
            continue
        if x == 2:
            continue
        if x == len(path) - 1:
            break
        if x == len(path) - 2:
            break
        if x == len(path) - 3:
            break
        path[media - x] = "..."
    if len(path[len(path) - 1]) > 35:
        path[len(path) - 1] = path[len(path) - 1][0:35] + "..."
    return path

compress_path()

class jsonEx:
    """
        Clase para dar soporte a los archivos de configuracion y la base de datos que contiene las extensiones
    """
    def update_json(filex,data) -> None:
        """
            Actualiza los datos de un archivo json. No devuelve nada
            filex: Archivo json
            data: Diccionario con configuraciones adentro
        """
        with open(filex,'w') as file:
            json.dump(data, file, indent=4)
        
    def get(filex) -> dict:
        """
            Obtiene los datos de un archivo json. Devuelve dict
            filex: Archivo json
        """
        with open(filex,'r') as file:
            return json.load(file)

class termui:
    """
        Clase para facilitar la escritura de un TUI
    """
    def terminal(opts, return_type=bool) -> int | bool:
        """
            Muestra un menu interactivo. Devuelve int o bool, por predeterminado int
            opts: Una lista conteniendo las opciones
            return_type (valor predeterminado bool): Especifica que quieres que se devuelva, bool para indicar si el primer elemento de la lista fue seleccionado e int para indicar que elemento de la lista se selecciono
        """
        if len(opts) < 1:
            raise IndexError("debug")
        menu = TerminalMenu(opts)
        if return_type == bool:
            return menu.show() == 0
        elif return_type == int:
            return menu.show()
        else:
            raise TypeError('Incompatible type')
    
termui().terminal()

class compress():
    """
        Clase para la facilitacion de la compresion de archivos, pronto con soporte para otros formatos
    """
    def __init__(self, filename : str, format="zip"):
        filename = os.path.splitext(filename)[0]
        if format == "zip":
            self.file = ZipFile(f'{filename}.{format}', 'w')
        else:
            self.file = ZipFile(f'{filename}.{format}', 'w')
    
    def _progress(current,max,label="",current_file=""):
        if current == max - 1:
            print(f"{label} ({max}/{max}) %100")
        else:
            if current_file != "":
                path = current_file.split('/')
                if len(path) >= 5:
                    print(f"{label} [{'/'.join(compress_path(path))}] ({current}/{max}) {int(current/max * 100)}%", end='\r')
            else:
                print(f"{label} ({current}/{max}) {int(current/max * 100)}%", end='\r')

    def add(self, files : list, callback=_progress):
        """
            Agrega archivos a un fichero zip. No devuelve nada
            files: Una lista conteniendo los archivos a comprimir
            callback=_progress: Un callback que se utilizara para mostrar el progreso, por defecto hay una funcion simple que muestra el progreso
        """
        if callback == None:
            for v,x in enumerate(files):
                self.file.write(x)
        else:
            for v,x in enumerate(files):
                self.file.write(x)
                callback(v,len(files),label="Comprimiendo...",current_file=x)
        print("")
    
    def add_single(self, files: str):
        """
            Agrega un solo archivo a un fichero zip. No devuelve nada
            files: Un archivo para ser comprimido
        """
        self.file.write(files)
    
    def finish(self):
        """
            IMPORTANTE EJECUTAR ESTO ya que si no lo ejecutas, el fichero estara incompleto
        """
        self.file.close()

class finder():
    """
        Clase para buscar archivos en el disco
    """
    def __init__(self, path, ext_list) -> None:
        if os.path.basename(path) != '':
            path = path + '/'
        self.path = path
        jsonxd = jsonEx.get('modules/exts.json')
        self.exts = jsonxd[ext_list]
    
    def find(self) -> dict:
        """
            Devuelve un diccionario conteniendo las extensiones junto con una lista de los archivos encontrados con su extension correspondiente
        """
        founded = {}
        self.all = []
        for x in self.exts:
            path = glob.glob(f"{self.path}**/*.{x}", recursive=True)
            if len(path) == 0:
                continue
            founded[x] = path
            for v in path:
                self.all.append(v)
        if len(founded) == 0:
            return 1
        return founded
    
    def find_userext(self,userext) -> dict:
        """
            Devuelve un diccionario conteniendo los archivos encontrados con la extension especificada
            userext: Extension con la que quieras buscar los archivos
        """
        founded = {}
        self.all = []
        path = glob.glob(f"{self.path}**/*.{userext}", recursive=True)
        if len(path) == 0:
            return 1
        founded[userext] = path
        self.all.extend(path)
        return founded
    
    def find_in_list(self,word,strict=False) -> list:
        """
            La funcion busca entre los archivos ya encontrados con la funcion find() con la variable word. Devuelve una lista
            word: Palabra por filtrar entre los archivos
            strict=False: Por defecto es falso, si es verdadero se usara una funcion para encontrar mas estrictamente entre los archivos
        """
        if not strict:
            word = os.path.splitext(word)[0]
            result = filter(lambda x: re.search("{}.*".format(word), x), self.all)
            result = list(result)
            return result
        else:
            ind = self.__findstrict(word)
            real = []
            for x in ind:
                real.append(self.all[x])
            return real
    
    def drive_format(self) -> dict:
        """
            Funcion para darle un formato especifico para usar con la clase Drive ({'names':[], 'paths':[]}). Devuelve dict
        """
        dictionary = {
            'names':[],
            'paths':[]
        }
        for x in self.all:
            dictionary['names'].append(os.path.basename(x))
            dictionary['paths'].append(x)
        return dictionary

    def generalize(self) -> list:
        """
            Funcion para convertir el diccionario con los archivos ordenados por extensiones a una lista. Devuelve una lista
        """
        return self.all

    def __findstrict(self,word) -> list:
        lowercase = list(map(lambda x: x.lower(), self.all))
        word = word.lower()
        ret = []
        for i, element in enumerate(lowercase):
            if re.search(f"{word}.*", element):
                ret.append(i)
        return ret

class files_handler:
    """
        Clase de funciones varias para manejar archivos
    """
    def wipe_txt(file: str):
        """
            Limpia un archivo de texto. No devuelve nada
            file: Ruta del archivo de texto
        """
        open(file,'w').close()
        
    def stat(file: str) -> list:
        """
            Funcion para devolver metadatos de un archivo. Devuelve list
            file: Archivo a analizar
        """
        stated = os.stat(file)
        name = os.path.basename(file)
        ext = os.path.splitext(name)
        return [name,file,ext[1],datetime.fromtimestamp(stated.st_mtime).strftime('%Y-%m-%d %H:%M'), stated.st_size / 1000000, stated.st_uid]
    def save(file: str, content: str | list):
        """
            Guarda un archivo con el contenido que especifiques (El contenido anterior del archivo se elimina). No devuelve nada
            file: Archivo a escribir
            content: Contenido 
        """
        if type(content) == list:
            files_handler.wipe_txt(file)
            with open(file,'a') as file:
                file.write(content[0])
                for v,x in enumerate(content):
                    if v == 0:
                        continue
                    file.write('\n' + x)
        elif type(content) == str:
            files_handler.wipe_txt(file)
            with open(file, 'w') as file:
                file.write(content)
        else:
            raise TypeError("Not str or list object")
                
                    


class Drive():
    """
        Clase para automatizar el logeo de Google Drive
    """
    def __init__(self, file=os.path.join(os.getenv('HOME'), '.local/share/secrets/.pydrive/.credentials.encrypt')):
        if os.path.exists(file):
            self.gauth = GoogleAuth()
            self.gauth.LoadCredentialsFile(file)
            os.system("./tests/main --create")
            os.system("./tests/main --load")
            self.gauth.LoadClientConfigFile(os.path.join(os.getenv('HOME'), '.local/share/secrets/.pydrive/.client_secrets.encrypt'))
            self.drive = GoogleDrive(self.gauth)
            os.system("./tests/main --create")
            self.credentials = file
        else:
            os.system("./tests/main --create")
            os.system("./tests/main --load")
            self.gauth = GoogleAuth()
            self.gauth.LoadClientConfigFile(os.path.join(os.getenv('HOME'), '.local/share/secrets/.pydrive/.client_secrets.encrypt'))
            self.gauth.LocalWebserverAuth()
            #os.system("./tests/main --create")
            print(file)
            os.system(f'mkdir -p {os.path.split(file)[0]}')
            self.gauth.SaveCredentialsFile(file)
            self.drive = GoogleDrive(self.gauth)
            self.credentials = file
        
    def __callbacks(current,max,label=""):
        if current == max - 1:
            print(f"{label} ({max}/{max}) %100")
        else:
            print(f"{label} ({current}/{max}) %{int(current/max * 100)}", end='\r')
    
    def user_info(self) -> dict:
        """
            Obtiene un diccionario conteniendo informacion del usuario. Devuelve dict
        """
        return self.drive.GetAbout()

    def create_folder(self,folder: str) -> int | str:
        """
            Crea una carpeta en la nube del usuario, si ya existe devuelve el id. Devuelve algo (No estoy seguro)
            folder: Nombre de la carpeta a crear
        """
        folder_list = self.drive.ListFile({'q': "mimeType='application/vnd.google-apps.folder' and trashed = false and title='"+folder+"'"}).GetList()
        if len(folder_list)>0:
            return folder_list[0]['id']
        else:
            folder_list = self.drive.CreateFile({'title': folder, "mimeType": "application/vnd.google-apps.folder"})
            folder_list.Upload()
            return folder_list['id']

    def upload(self, name: str, content: str, folder: str, label="Subiendo...", endx='\n'):
        """
            Funcion para subir un solo archivo a Google Drive. No devuelve nada
            name: Nombre del archivo
            content: Ruta del archivo
            folder: ID de la carpeta en donde se subira el archivo
            label="Subiendo...": Etiqueta que se imprimira en la terminal, puedes dejarlo como una cadena vacia
            endx='\n': Se pondra al final de print(), puedes dejarlo como una cadena vacia
        """
        filex = self.drive.CreateFile({'title': name, 'parents': [{'id': folder}]})
        filex.SetContentFile(content) # especificar la ruta del archivo en tu computadora
        print(label, end=endx)
        filex.Upload()
    
    def uploads(self, files: dict, folder: str, callback=__callbacks):
        """
            Funcion para subir varios archivos a Google Drive. No devuelve nada
            files: Diccionario conteniendo los nombres y las rutas de los archivos (Ejemplo: {'names':[], 'paths':[]})
            folder: ID de la carpeta en donde se subiran los archivos
            callback=__callbacks: Funcion callback que se utilizara para mostrar el progreso de subida de archivos
        """
        for v,x in enumerate(files['names']):
            file = self.drive.CreateFile({'title': x, 'parents': [{'id': folder}]})
            file.SetContentFile(files['paths'][v]) # especificar la ruta del archivo en tu computadora
            callback(v,len(files['names']),label="Subiendo archivos")

            file.Upload()

def printc(msg,color, endx='\n', label="[INFO]"):
    print(Colorate.Horizontal(color, label), msg, end=endx)

__all__ = ["finder.__finderstrict"]