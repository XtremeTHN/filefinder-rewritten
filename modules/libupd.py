import requests as rq
import json, os
class UrlExceptions(Exception):
    class UrlNotSecure(Exception):
        pass
    class NotAnUrl(Exception):
        pass
    class UnknownUrlError(Exception):
        pass

class libupd():
    def __init__(self,url) -> None:
        if not isinstance(url, list):
            raise TypeError("List esperado, tipo de dato dado:{}".format(type(url)))
        for x in url:
            if not isinstance(x,str):
                raise TypeError("String esperado en un elemento de la lista dada, tipo de dato dado:{}".format(type(x)))

            if x[0:8] != "https://":
                raise UrlExceptions.UrlNotSecure("Una de las url no contiene https:// al principio")
        self.url = [self.__connect(url[0]), self.__connect(url[1])]

        if isinstance(self.url[0],tuple) or isinstance(self.url[1],tuple) in [True,True]:
            raise UrlExceptions.UnknownUrlError("Error desconocido. Debug data: {}".format(self.url))
    def __connect(self,url):
        try:
            code = rq.get(url)
            if code.status_code == 200:
                return code
            else:
                return (1,code.status_code)
        except:
            return (2,code.status_code)
    
    def checkupd(self,version) -> int:
        if not isinstance(version,(float,int)):
            raise TypeError("El argumento debe de ser tipo integer o float")
        content = self.url[0].content.decode("utf-8")
        if float(content) > float(version):
            return 1
        else:
            return 0
    def update(self, path=os.getcwd()):
        database = json.loads(self.url[1].content)
        for x in database:
            web_file = rq.get(database[x]).content
            with open(os.path.join(path, x),'wb') as file:
                file.write(web_file)    

    def close(self):
        self.url[0].close()
        self.url[1].close()

__all__ = ['libupd.__connect']