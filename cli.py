import argparse
import sys
 
from extraccion import extraer_de_directorio, extraer_de_codigo, buscar_funcion
from similitud import similitud, es_candidata_a_duplicado, UMBRAL
 
# Lee los argumentos de la línea de comandos y devuelve un objeto con los valores.
def leer_argumentos():
    parser = argparse.ArgumentParser(
        description="Busca funciones estructuralmente similares a una función dada."
    )
    parser.add_argument("--dir", required=True,
                        help="carpeta donde buscar")
    parser.add_argument("--funcion",
                        help="función objetivo, con el formato archivo.py:nombre")
    parser.add_argument("--top", type=int, default=5,
                        help="cantidad de resultados a mostrar (por defecto 5)")
    return parser.parse_args()
 
# Devuelve la función objetivo (diccionario) o None si no se encontró.
def obtener_objetivo(args, funciones):
    if args.funcion:
        # rsplit separa por el ÚLTIMO ":" 
        if ":" not in args.funcion:
            print("Error: --funcion tiene que tener el formato archivo.py:nombre")
            return None
        archivo, nombre = args.funcion.rsplit(":", 1)
        objetivo = buscar_funcion(funciones, archivo, nombre)
        if objetivo is None:
            print(f"Error: no se encontró la función '{nombre}' en '{archivo}'")
        return objetivo
 
    # si no se pasó --funcion, se pega el código
    print("Pegá el código de la función y terminá con Ctrl+D (Ctrl+Z y Enter en Windows):")
    codigo = sys.stdin.read()
    try:
        funciones_pegadas = extraer_de_codigo(codigo)
    except SyntaxError:
        print("Error: el código pegado tiene errores de sintaxis")
        return None
    if not funciones_pegadas:
        print("Error: el código pegado no tiene ninguna función")
        return None
    return funciones_pegadas[0]
 
# Compara el objetivo contra todas las funciones y devuelve las top más similares.
def buscar(objetivo, funciones, top):
    resultados = []
    for funcion in funciones:
        # no comparamos la función consigo misma
        if funcion["archivo"] == objetivo["archivo"] and funcion["linea"] == objetivo["linea"]:
            continue
        score = similitud(objetivo["nodo"], funcion["nodo"])
        resultados.append((score, funcion))
 
    # ordenamos de mayor a menor score
    resultados.sort(key=lambda r: r[0], reverse=True)
    return resultados[:top]
 
# Muestra los resultados en pantalla.
def mostrar(objetivo, resultados):
    print()
    print(f"Función objetivo: {objetivo['nombre']} ({objetivo['archivo']}, línea {objetivo['linea']})")
    print(f"Umbral de duplicado: {UMBRAL}")
    print()
    if not resultados:
        print("No hay otras funciones para comparar.")
        return
    for posicion, (score, funcion) in enumerate(resultados, start=1):
        marca = "  <-- posible duplicado" if es_candidata_a_duplicado(score) else ""
        print(f"{posicion}. {score:.2f}  {funcion['nombre']} "
              f"({funcion['archivo']}, línea {funcion['linea']}){marca}")
 
# Función principal: lee argumentos, busca y muestra resultados. 
def main():
    args = leer_argumentos()
    funciones = extraer_de_directorio(args.dir)
    print(f"Se encontraron {len(funciones)} funciones en {args.dir}")
 
    objetivo = obtener_objetivo(args, funciones)
    if objetivo is None:
        return
 
    resultados = buscar(objetivo, funciones, args.top)
    mostrar(objetivo, resultados)
 
# Ejecuta la función principal si se ejecuta este archivo directamente.
if __name__ == "__main__":
    main()