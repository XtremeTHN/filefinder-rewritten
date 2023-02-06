import json, glob, os, re, sys
from simple_term_menu import TerminalMenu
from pystyle import Colorate
from zipfile import ZipFile
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from statistics import median
from datetime import datetime


def compress_path(path: list):
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
    

class jsonEx:
    def update_json(filex,data) -> None:
        with open(filex,'w') as file:
            json.dump(data, file, indent=4)
        
    def get(filex):
        with open(filex,'r') as file:
            return json.load(file)

class termui:
    def terminal(opts, return_type=bool):
        if len(opts) < 1:
            raise IndexError("debug")
        menu = TerminalMenu(opts)
        if return_type == bool:
            return menu.show() == 0
        elif return_type == int:
            return menu.show()
        else:
            raise TypeError('Incompatible type')

class compress():
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
        for v,x in enumerate(files):
            self.file.write(x)
            callback(v,len(files),label="Comprimiendo...",current_file=x)
        print("")
    
    def finish(self):
        self.file.close()

class finder():
    def __init__(self, path, ext_list) -> None:
        if os.path.basename(path) != '':
            path = path + '/'
        self.path = path
        jsonxd = jsonEx.get('modules/exts.json')
        self.exts = jsonxd[ext_list]
    
    def find(self) -> dict:
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
        founded = {}
        self.all = []
        path = glob.glob(f"{self.path}**/*.{userext}", recursive=True)
        if len(path) == 0:
            return 1
        founded[userext] = path
        self.all.extend(path)
        return founded
    
    def find_in_list(self,word,strict=False) -> list:
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
        dictionary = {
            'names':[],
            'paths':[]
        }
        for x in self.all:
            dictionary['names'].append(os.path.basename(x))
            dictionary['paths'].append(x)
        print(dictionary)
        return dictionary

    def generalize(self) -> list:
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
    "Mueve archivos"
    def move(src: list, dest: str):
        pass
    def stat(file: str) -> list:
        stated = os.stat(file)
        name = os.path.basename(file)
        ext = os.path.splitext(name)
        return [name,file,ext[1],datetime.fromtimestamp(stated.st_mtime).strftime('%Y-%m-%d %H:%M'), stated.st_size / 1000000, stated.st_uid]


class Drive():
    def __init__(self, file=os.path.join(os.getenv('HOME'), '.local/share/secrets/.pydrive/.credentials.encrypt')):
        if os.path.exists(file):
            self.gauth = GoogleAuth()
            self.gauth.LoadCredentialsFile(file)
            os.system("./tests/main --create")
            os.system("./tests/main --load")
            self.gauth.LoadClientConfigFile(os.path.join(os.getenv('HOME'), '.local/share/secrets/.pydrive/.client_secrets.encrypt'))
            self.drive = GoogleDrive(self.gauth)
            os.system("./tests/main --create")
        else:
            os.system("./tests/main --create")
            os.system("./tests/main --load")
            self.gauth = GoogleAuth()
            self.gauth.LoadClientConfigFile(os.path.join(os.getenv('HOME'), '.local/share/secrets/.pydrive/.client_secrets.encrypt'))
            self.gauth.LocalWebserverAuth()
            os.system("./tests/main --create")
            os.system(f'mkdir -p {os.path.split(file)[0]}')
            self.gauth.SaveCredentialsFile(file)
            self.drive = GoogleDrive(self.gauth)
        
    def __callbacks(current,max,label=""):
        if current == max - 1:
            print(f"{label} ({max}/{max}) %100")
        else:
            print(f"{label} ({current}/{max}) %{int(current/max * 100)}", end='\r')
    

    def create_folder(self,folder: str):
        folder_list = self.drive.ListFile({'q': "mimeType='application/vnd.google-apps.folder' and trashed = false and title='"+folder+"'"}).GetList()
        if len(folder_list)>0:
            return folder_list[0]['id']
        else:
            folder_list = self.drive.CreateFile({'title': folder, "mimeType": "application/vnd.google-apps.folder"})
            folder_list.Upload()
            return folder_list['id']

    def upload(self, filexd: dict, folder: str, label="Subiendo..."):
        filex = self.drive.CreateFile({'title': filexd['names'], 'parents': [{'id': folder}]})
        filex.SetContentFile(filexd['paths']) # especificar la ruta del archivo en tu computadora
        print(label)
        filex.Upload()
    
    def uploads(self, files: dict, folder: str, callback=__callbacks):
        for v,x in enumerate(files['names']):
            file = self.drive.CreateFile({'title': x, 'parents': [{'id': folder}]})
            file.SetContentFile(files['paths'][v]) # especificar la ruta del archivo en tu computadora
            file.Upload()
            callback(v,len(files['names']),label="Subiendo archivos")

def printc(msg,color, endx='\n', label="[INFO]"):
    print(Colorate.Horizontal(color, label), msg, end=endx)

__all__ = ["finder.__finderstrict"]