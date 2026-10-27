import ast
import os
 
# Extrae funciones de código Python, ya sea de un string, un archivo o un directorio completo.
def extraer_de_codigo(codigo, archivo="<pegado>"):
    """Parsea un string de código y devuelve la lista de funciones que contiene."""
    arbol = ast.parse(codigo)  # genera el árbol sintáctico (AST) del código
    funciones = []
 
    # ast.walk recorre TODOS los nodos del árbol
    for nodo in ast.walk(arbol):
        if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
            funciones.append({
                "nombre": nodo.name, # nombre de la función
                "archivo": archivo, # nombre del archivo donde se encuentra
                "linea": nodo.lineno, # número de línea donde se define la función
                "nodo": nodo, # el nodo AST de la función
            })
 
    return funciones
 
# Extrae funciones de un archivo .py
def extraer_de_archivo(ruta, nombre_archivo=None):
    """Lee un archivo .py y devuelve sus funciones."""
    if nombre_archivo is None:
        nombre_archivo = ruta
 
    with open(ruta, "r", encoding="utf-8") as f:
        codigo = f.read()
 
    return extraer_de_codigo(codigo, nombre_archivo)
 
# Extrae funciones de todos los archivos .py en un directorio
def extraer_de_directorio(directorio):
    """Recorre recursivamente el directorio y devuelve las funciones de todos los .py."""
    funciones = []
 
    # os.walk recorre el directorio y todos sus subdirectorios
    for carpeta, subcarpetas, archivos in os.walk(directorio):
        for nombre in archivos:
            if nombre.endswith(".py"):
                ruta = os.path.join(carpeta, nombre)
                ruta_relativa = os.path.relpath(ruta, directorio)
                try:
                    funciones.extend(extraer_de_archivo(ruta, ruta_relativa))
                except SyntaxError:
                    # si un archivo tiene errores de sintaxis, lo salteamos
                    print(f"Aviso: no se pudo parsear {ruta_relativa}")
 
    return funciones
 
 
def buscar_funcion(funciones, archivo, nombre):
    """Busca una función por archivo y nombre. Devuelve None si no la encuentra."""
    for funcion in funciones:
        if funcion["archivo"] == archivo and funcion["nombre"] == nombre:
            return funcion
    return None
 