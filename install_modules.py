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
        from pystyle import Colors
    except ImportError:
        import os,sys
        os.system("pip3 install pystyle")
        try:
            import pystyle
        except ImportError:
            print("[INFO] No se pudo inicializar la decoracion, debido a que el modulo pystyle no esta disponible")
            print("[INFO] Si deseas desactivar esto, ejecuta la instalacion con 'unable pystyle")
            sys.exit(1)
    try:
        from modules.funcs import printc
    except:
        print("[INFO] Asegurate de estar en la misma carpeta donde filefinder esta ubicado")
        sys.exit(1)

def execute(module):
    if "output" in sys.argv:
        os.system(f"pip3 install {module}")
    else:
        os.system(f"pip3 install {module} > /dev/null")

modules = ['pystyle', 'simple_term_menu', 'zipfile', 'pydrive2', 'statistics', 'shutil', 'requests', 'pygobject', 'argparse']
path = os.path.join(os.getenv("HOME"), ".local", "bin", "finder")
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
printc(f"Instalado correctamente!", Colors.blue_to_green)