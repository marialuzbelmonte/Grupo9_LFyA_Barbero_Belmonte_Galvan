import ast
 
from normalizacion import normalizar
 
N = 3          # tamaño de los n-gramas
UMBRAL = 0.7  # a partir de este score dos funciones son "candidatas a duplicado"
 
# Devuelve el conjunto de nombres que son parámetros o variables de la función.
def serializar(nodo):
    # Recorre el árbol en pre-order y devuelve la lista de tokens.
    
    # 1) primero el nodo actual: su tipo (ej: "Assign", "For", "BinOp")
    tokens = [type(nodo).__name__]
 
    # además, para algunos nodos agregamos su valor normalizado.
    # A las variables les sacamos el número (VAR3 -> VAR): el número depende
    # del orden en que aparecen, y si se reordenan líneas cambiaría.
    if isinstance(nodo, ast.Name):
        if nodo.id.startswith("VAR"):
            tokens.append("VAR")
        else:
            tokens.append(nodo.id)          # print, len, range, etc.
    elif isinstance(nodo, ast.arg):
        tokens.append("VAR")
    elif isinstance(nodo, ast.Constant):
        tokens.append(str(nodo.value))      # LIT
 
    # 2) después los hijos, de izquierda a derecha (recursivo)
    for hijo in ast.iter_child_nodes(nodo):
        # Load / Store solo indican si la variable se lee o se escribe: no aportan
        if isinstance(hijo, ast.expr_context):
            continue
        tokens.extend(serializar(hijo))
 
    return tokens
 
# Devuelve el conjunto de nombres que son parámetros o variables de la función.
def ngramas(tokens, n=N):
    # Devuelve el CONJUNTO de n-gramas (tuplas de n tokens seguidos).
    if len(tokens) < n:
        return {tuple(tokens)}
    resultado = set()
    for i in range(len(tokens) - n + 1):
        resultado.add(tuple(tokens[i:i + n]))
    return resultado
 
# Devuelve el score de similitud entre dos funciones (recibe sus subárboles AST).
def jaccard(conjunto_a, conjunto_b):
    # Similitud de Jaccard: |A ∩ B| / |A ∪ B|. Da un valor entre 0 y 1.
    union = conjunto_a | conjunto_b
    if not union:
        return 1.0
    interseccion = conjunto_a & conjunto_b
    return len(interseccion) / len(union)
 
# Devuelve el conjunto de nombres que son parámetros o variables de la función.
def tokens_de_funcion(nodo_funcion):
    # Normaliza el subárbol de una función y lo serializa.
    return serializar(normalizar(nodo_funcion))
 
# Devuelve el score de similitud entre dos funciones (recibe sus subárboles AST).
def similitud(nodo_a, nodo_b, n=N):
    # Score de similitud entre dos funciones (recibe sus subárboles AST).
    tokens_a = tokens_de_funcion(nodo_a)
    tokens_b = tokens_de_funcion(nodo_b)
    return jaccard(ngramas(tokens_a, n), ngramas(tokens_b, n))
 
# Devuelve True si el score indica que las funciones son "candidatas a duplicado".
def es_candidata_a_duplicado(score):
    return score >= UMBRAL