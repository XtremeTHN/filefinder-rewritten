import json, glob, os, re
from simple_term_menu import TerminalMenu
from pystyle import Colorate

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

class finder():
    def __init__(self, path, ext_list):
        
        if os.path.basename(path) != '':
            path = path + '/'
        self.path = path
        jsonxd = jsonEx.get('modules/exts.json')
        self.exts = jsonxd[ext_list]
        
    
    def find(self):
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
    
    def find_userext(self,userext):
        founded = {}
        self.all = []
        path = glob.glob(f"{self.path}**/*.{userext}", recursive=True)
        if len(path) == 0:
            return 1
        founded[userext] = path
        self.all.extend(path)
        return founded
    
    def find_in_list(self,word,strict=False):
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

    def __findstrict(self,word):
        lowercase = list(map(lambda x: x.lower(), self.all))
        word = word.lower()
        ret = []
        for i, element in enumerate(lowercase):
            if re.search(f"{word}.*", element):
                ret.append(i)
        return ret

            

def printc(msg,color, endx='\n'):
    print(Colorate.Horizontal(color, "[INFO]"), msg, end=endx)