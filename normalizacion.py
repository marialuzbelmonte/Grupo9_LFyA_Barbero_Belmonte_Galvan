import ast
import copy
 
# Devuelve el conjunto de nombres que son parámetros o variables de la función.
def encontrar_locales(nodo_funcion):
    locales = set()
    for nodo in ast.walk(nodo_funcion):
        if isinstance(nodo, ast.arg): 
            locales.add(nodo.arg)  
        elif isinstance(nodo, ast.Name) and isinstance(nodo.ctx, ast.Store):
            locales.add(nodo.id)  
    return locales
 
# Devuelve el conjunto de nombres que son parámetros o variables de la función.
class Normalizador(ast.NodeTransformer):
    
    #Recorre el árbol y va reemplazando los nodos que hay que normalizar.
    def __init__(self, nombre_funcion, locales):
        self.nombre_funcion = nombre_funcion
        self.locales = locales
        self.mapeo = {}  # de nombre original a token genérico 
    
    # Devuelve el token de una variable, creándolo si es la primera vez que aparece.
    def nombre_generico(self, nombre):
        # Devuelve el token de una variable, creándolo si es la primera vez que aparece.
        if nombre not in self.mapeo:
            self.mapeo[nombre] = "VAR" + str(len(self.mapeo) + 1)
        return self.mapeo[nombre]

    # Reemplaza el nombre de la función por "FUNC" y elimina el docstring si lo hay.
    def visit_FunctionDef(self, nodo):
        nodo.name = "FUNC"
 
        # si el primer elemento del cuerpo es un string suelto, es el docstring: lo sacamos
        primero = nodo.body[0]
        if (len(nodo.body) > 1
                and isinstance(primero, ast.Expr)
                and isinstance(primero.value, ast.Constant)
                and isinstance(primero.value.value, str)):
            nodo.body = nodo.body[1:]
 
        self.generic_visit(nodo)  # sigue recorriendo los hijos
        return nodo
 
    # las funciones async se tratan igual que las normales
    visit_AsyncFunctionDef = visit_FunctionDef

    # Reemplaza los nombres de los parámetros por tokens genéricos.
    def visit_arg(self, nodo):
        nodo.arg = self.nombre_generico(nodo.arg)
        self.generic_visit(nodo)
        return nodo

    # Reemplaza los nombres de las variables locales por tokens genéricos.
    def visit_Name(self, nodo):
        if nodo.id in self.locales:
            nodo.id = self.nombre_generico(nodo.id)
        elif nodo.id == self.nombre_funcion:
            nodo.id = "FUNC"  # llamada recursiva a sí misma
        return nodo

    # Reemplaza los literales por "LIT"
    def visit_Constant(self, nodo):
        nodo.value = "LIT"
        return nodo
 
# Normaliza un nodo de función, devolviendo una copia normalizada del subárbol (el original no se toca).
def normalizar(nodo_funcion):
    copia = copy.deepcopy(nodo_funcion)
    locales = encontrar_locales(copia)
    normalizador = Normalizador(copia.name, locales)
    return normalizador.visit(copia)