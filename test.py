import ast
 
from similitud import similitud, UMBRAL
 
# Parsea el código y devuelve el subárbol de la función (el primer elemento del módulo).
def arbol_funcion(codigo):
    modulo = ast.parse(codigo)
    return modulo.body[0]
 
# Devuelve el score de similitud entre dos funciones escritas como texto.
def comparar(codigo1, codigo2):
    return similitud(arbol_funcion(codigo1), arbol_funcion(codigo2))
 
 
# --- CASOS POSITIVOS ---
 
def test_clon_variables_renombradas():
    # Función original: cuenta cuántos números positivos hay en una lista
    f1 = """
def contar_positivos(numeros):
    cantidad = 0
    for n in numeros:
        if n > 0:
            cantidad = cantidad + 1
    return cantidad
"""
    # Misma función con otro nombre y otras variables
    f2 = """
def cuantos_mayores(lista):
    c = 0
    for x in lista:
        if x > 0:
            c = c + 1
    return c
"""
    score = comparar(f1, f2)
 
    # Después de normalizar los dos árboles quedan iguales
    assert score == 1.0
    assert score >= UMBRAL
 
 
def test_clon_lineas_reordenadas():
    # Función original: calcula el precio final de una compra
    f1 = """
def precio_final(precio, cantidad):
    subtotal = precio * cantidad
    descuento = subtotal * 0.1
    envio = 500
    return subtotal - descuento + envio
"""
    # Misma función con las líneas de "envio" y "descuento" en otro orden
    # (y con otros nombres)
    f2 = """
def total_compra(p, cant):
    sub = p * cant
    costo_envio = 500
    desc = sub * 0.1
    return sub - desc + costo_envio
"""
    score = comparar(f1, f2)
 
    # Jaccard compara conjuntos de trigramas, así que el orden de las líneas
    # casi no influye: tiene que superar el umbral
    assert score >= UMBRAL
 
 
# --- CASOS NEGATIVOS ---
 
def test_funciones_totalmente_distintas():
    # Invierte una palabra usando un bucle while
    f1 = """
def invertir(palabra):
    resultado = ""
    i = len(palabra) - 1
    while i >= 0:
        resultado = resultado + palabra[i]
        i = i - 1
    return resultado
"""
    # Arma un diccionario con datos de una persona
    f2 = """
def crear_persona(nombre, edad):
    return {"nombre": nombre, "edad": edad, "activo": True}
"""
    score = comparar(f1, f2)
 
    # No comparten casi ninguna estructura
    assert score < 0.25
    assert score < UMBRAL
 
 
def test_funciones_parecidas_pero_distintas():
    # Suma todos los elementos de una lista
    f1 = """
def sumar(lista):
    total = 0
    for e in lista:
        total = total + e
    return total
"""
    # Busca el máximo de una lista: también tiene un for sobre la lista,
    # pero adentro hace otra cosa (un if en lugar de una suma)
    f2 = """
def maximo(lista):
    mayor = lista[0]
    for e in lista:
        if e > mayor:
            mayor = e
    return mayor
"""
    score = comparar(f1, f2)
 
    # Comparten parte de la estructura (por eso el score no es bajo),
    # pero no alcanzan el umbral
    assert score > 0.25
    assert score < UMBRAL
 