import json, glob, os, re
from simple_term_menu import TerminalMenu
from pystyle import Colorate
from zipfile import ZipFile

def _progress(current,max,label=""):
    print(f"{label} ({current}/{max}) %{int(current/max * 100)}", end='\r')

class jsonEx:
    def update_json(filex,data) -> None:
        with open(filex,'w') as file:
            json.dump(data, file, indent=4)
        
    def get(filex):
        with open(filex,'r') as file:
            return json.load(file)

class termui:
    def terminal(opts):
        if len(opts) < 1:
            raise IndexError("debug")
        menu = TerminalMenu(opts)
        return menu.show()

class compress():
    def __init__(self, filename : str, format="zip"):
        filename = os.path.splitext(filename)[0]
        if format == "zip":
            self.file = ZipFile(f'{filename}.{format}', 'w')

    def add(self, files : list, callback=_progress):
        for v,x in enumerate(files):
            self.file.write(x)
            callback(v,len(files),label="Comprimiendo...")
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

__all__ = ["finder.__finderstrict"]


def printc(msg,color, endx='\n', label="[INFO]"):
    print(Colorate.Horizontal(color, label), msg, end=endx)

