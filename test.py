from modules.funcs import Drive

info = Drive().user_info()

for x in info:
    print("Nombre: ",x, "Tipo: ",type(info[x]), "Salto de linea: \n")
    print(info[x])

print()
print("Informacion especifica:", info['user']['picture']['url'])