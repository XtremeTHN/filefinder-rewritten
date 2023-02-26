import sys, os
PYSTYLE = True
for x in sys.argv:
    if x == "unable":
        def printc(msg,color, endx='\n', label="[INFO]"):
            print(label, msg, end=endx)
        class Colors:
            green_to_blue = ""
            blue_to_green = ""
        PYSTYLE = False
if PYSTYLE:
    try:
        from pystyle import Colorate, Colors
    except ImportError:
        import os,sys
        os.system("pip3 install pystyle")
        try:
            from pystyle import Colorate, Colors
        except ImportError:
            print("[INFO] No se pudo inicializar la decoracion, debido a que el modulo pystyle no esta disponible")
            print("[INFO] Si deseas desactivar esto, ejecuta la instalacion con 'unable pystyle")
            sys.exit(1)
    def printc(msg,color, endx='\n', label="[INFO]"):
        print(Colorate.Horizontal(color, label), msg, end=endx)

def execute(module):
    if "output" in sys.argv:
        os.system(f"pip3 install {module}")
    else:
        os.system(f"pip3 install {module} > /dev/null")

modules = ['pystyle', 'simple_term_menu', 'pydrive2', 'statistics', 'requests', 'pygobject', 'argparse']
path = os.path.join(os.getenv("HOME"), ".local", "bin", "finder")
printc("Instalando dependencias...", Colors.green_to_blue)
code = os.system("sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 > /dev/null")
if code > 0:
    printc("Hubo un error instalando las dependencias... Error: {}".format(code), Colors.red_to_blue, label="[ERR]")
    printc("Si lo necesitas, puedes visitar este link para obtener ayuda para instalar los modulos (solo algunos estan listados)")
    print("https://github.com/XtremeTHN/filefinder-rewritten/blob/main/MODULES.md")
    sys.exit(code)
printc("Instalando modulos...", Colors.green_to_blue)
for x,v in enumerate(modules):
    printc(f"Instalando modulos... {v} {int(x / len(modules) * 100)}%", Colors.green_to_blue)
    execute(v)
# Esto no hace nada que sirva, ya que al cambiar el directorio de trabajo en main.py sigue sin reconocer el modulo modules.funcs
"""printc(f"Creando comando global...", Colors.green_to_blue)
os.system(f"ln {os.path.join(os.getcwd(),'main.py')} {path}")
os.system(f"chmod +x {path}")
if os.getenv('SHELL') == "/usr/bin/zsh":
    resource = open(os.path.join(os.getenv("HOME"), ".zshrc"), 'a')
elif os.getenv('SHELL') == "/usr/bin/bash":
    resource = open(os.path.join(os.getenv("HOME"), ".bashrc"), 'a')

resource.write(f"\nexport FINDER_PATH={os.getcwd()}")
resource.close()"""
printc("Si ha habido un error durante la instalacion de cualquiera de los modulos, puedes ir a este link para instalar los modulos manualmente:", Colors.green_to_blue)
print("https://github.com/XtremeTHN/filefinder-rewritten/blob/main/MODULES.md")
printc(f"Instalado correctamente!", Colors.blue_to_green)