"""
Proyecto Final de Python:
Sistema de eliminación de archivos duplicados.

Este script analiza una carpeta, detecta archivos duplicados
comparando su contenido y elimina las copias antiguas,
conservando siempre la versión más reciente.
"""

import os
import hashlib
from datetime import datetime


def obtener_hash(ruta_archivo):
    """
    Calcula el hash del archivo usando hashlib.

    El hash funciona como una "huella digital" del contenido
    del archivo. Si dos archivos tienen el mismo hash, se
    considera que su contenido es idéntico.
    """
    sha = hashlib.sha256()

    try:
        with open(ruta_archivo, "rb") as archivo:
            # Leemos el archivo en bloques para no cargarlo todo a memoria
            while True:
                bloque = archivo.read(4096)
                if not bloque:
                    break
                sha.update(bloque)
    except Exception as error:
        print(f"No se pudo leer el archivo: {ruta_archivo} ({error})")
        return None

    return sha.hexdigest()


def buscar_duplicados(carpeta):
    """
    Recorre la carpeta indicada y busca archivos duplicados.

    Devuelve un diccionario donde:
    - clave: hash del archivo
    - valor: lista de rutas de archivos que comparten ese hash
    (solo se incluyen los que realmente están duplicados).
    """
    duplicados = {}
    print("\nEscaneando archivos...\n")

    for ruta_actual, _, archivos in os.walk(carpeta):
        for nombre in archivos:
            ruta_completa = os.path.join(ruta_actual, nombre)
            hash_archivo = obtener_hash(ruta_completa)

            # Si no se pudo calcular el hash, se omite el archivo
            if hash_archivo is None:
                continue

            if hash_archivo not in duplicados:
                duplicados[hash_archivo] = []

            duplicados[hash_archivo].append(ruta_completa)

    # Filtrar: nos quedamos solo con los que tienen más de un archivo
    duplicados = {
        h: rutas for h, rutas in duplicados.items() if len(rutas) > 1
    }

    print("Búsqueda de duplicados completada.\n")
    return duplicados


def archivo_mas_reciente(rutas):
    """
    Recibe una lista de rutas de archivos duplicados y devuelve:

    - mas_reciente: ruta del archivo más reciente.
    - copias: lista de rutas de los archivos que se consideran copias
      antiguas y que se pueden eliminar.
    """
    rutas_con_fechas = []

    for ruta in rutas:
        try:
            fecha_modificacion = os.path.getmtime(ruta)
        except Exception:
            # Si ocurre algún error, se marca con fecha 0 (muy antiguo)
            fecha_modificacion = 0

        rutas_con_fechas.append((ruta, fecha_modificacion))

    # Seleccionamos el archivo con la fecha de modificación más reciente
    mas_reciente = max(rutas_con_fechas, key=lambda x: x[1])[0]

    # Todo lo que NO es el más reciente se marca como copia
    copias = [ruta for ruta in rutas if ruta != mas_reciente]

    return mas_reciente, copias


def eliminar_duplicados(duplicados):
    """
    Elimina las copias antiguas de cada grupo de archivos duplicados.

    Siempre conserva el archivo más reciente y elimina el resto.
    Muestra por pantalla lo que se conserva y lo que se elimina.
    """
    total_eliminados = 0
    numero_grupo = 1

    for hash_valor, rutas in duplicados.items():
        print(f"--- GRUPO {numero_grupo} ---")
        mas_reciente, copias = archivo_mas_reciente(rutas)

        print("Se conservará (más reciente):")
        print(f"  {mas_reciente}")
        print("Se eliminarán las siguientes copias:")

        for copia in copias:
            print(f"  {copia}")

        # Eliminación física de los archivos marcados como copia
        for copia in copias:
            try:
                os.remove(copia)
                print(f"  Eliminado: {copia}")
                total_eliminados += 1
            except Exception as error:
                print(f"  Error al eliminar {copia}: {error}")

        print()  # línea en blanco entre grupos
        numero_grupo += 1

    print(
        f"\nProceso completado. "
        f"Total de archivos eliminados: {total_eliminados}"
    )


def mostrar_duplicados_encontrados(duplicados):
    """
    Muestra por pantalla todos los archivos que fueron
    detectados como duplicados, junto con su fecha de modificación.
    """
    print("Archivos duplicados encontrados:\n")

    for rutas in duplicados.values():
        for ruta in rutas:
            try:
                fecha = os.path.getmtime(ruta)
                fecha_legible = datetime.fromtimestamp(
                    fecha
                ).strftime("%Y-%m-%d %H:%M")
            except Exception:
                fecha_legible = "desconocida"

            print(f"  {ruta}")
            print(f"     Última modificación: {fecha_legible}")
        print()  # línea en blanco entre grupos


def main():
    """
    Función principal del programa.

    Pide al usuario la ruta de la carpeta a analizar,
    busca archivos duplicados y, si el usuario lo confirma,
    elimina las copias antiguas.
    """
    print("=== Proyecto Final: Eliminación de Archivos Duplicados ===\n")

    carpeta = input(
        "Ingrese la ruta de la carpeta a analizar: "
    ).strip().strip('"')

    if not os.path.isdir(carpeta):
        print("La ruta ingresada no es válida.")
        return

    duplicados = buscar_duplicados(carpeta)

    if not duplicados:
        print("No se encontraron archivos duplicados.")
        return

    mostrar_duplicados_encontrados(duplicados)

    confirmar = input(
        "¿Desea eliminar las copias antiguas y conservar solo "
        "la versión más reciente? (si/no): "
    ).strip().lower()

    if confirmar == "si":
        eliminar_duplicados(duplicados)
    else:
        print("Operación cancelada. No se eliminaron archivos.")


if __name__ == "__main__":
    main()
