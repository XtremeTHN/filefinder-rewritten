# FileSeeker

Mismo buscador de archivos de Python, pero ahora escrito en Rust y la busqueda es 2 veces mas rapida, por ahora las capacidades son limitadas.
Solo puede buscar archivos, filtrar por coincidencias y mostrar resultados sin formateo para usar con comandos como cp, mv, rm, tar, zip, etc.

## Requisitos

Para ejecutar este programa se requiere tener instalado Rust en el sistema, debido a que por ahora, no habran archivos binarios ya compilados.

## Uso

El programa se puede ejecutar en la terminal con el comando ./finder [opciones].
Opciones

    -f, --find: Busca archivos especificando la categoría de extensiones que desees buscar.
    -p, --path: Especifica la carpeta en donde buscar, por defecto es la carpeta actual de trabajo.
    -s, --search: Busca coincidencias entre los archivos encontrados.
    --no-formating: Imprime los resultados sin formatear el texto.

## Ejemplo de Uso

Asumiendo que el programa ya fue compilado con cargo build, asi se puede usar el programa

Para buscar archivos con extensión .txt en la carpeta actual, se debe ejecutar:

  ./finder -f txt

Para buscar archivos con extensión .rs en la carpeta /home/usuario/proyectos, se debe ejecutar:

  ./finder -f rs -p /home/usuario/proyectos

Para buscar archivos con extensión .txt que contengan la palabra hola en la carpeta actual, se debe ejecutar:

  ./finder -f txt -s hola

Para buscar archivos con extensión .txt que contengan la palabra hola en la carpeta actual y mostrar los resultados sin formatear el texto, se debe ejecutar:

  ./finder -f txt -s hola --no-formating
