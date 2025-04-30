#!/usr/bin/env python3
import sys
import os
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from config_db import get_connection


# Validación de argumentos
if len(sys.argv) < 4:
    print("Uso: {} <archivo_log> <nombre_programa_db> <session_id>".format(sys.argv[0]))
    exit(1)

LOG_FILE = sys.argv[1]
programa = sys.argv[2]

# Validar que session_id sea un número entero
try:
    session_id = int(sys.argv[3])
except ValueError:
    print("El ID de sesión debe ser un número entero.")
    exit(1)

lista_inputs = []
lista_salidas = []

hora_inicio = None
hora_fin = None

# Procesar el archivo de log
try:
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("Servidor iniciado:"):
                if hora_inicio is None:
                    hora_inicio = line.replace("Servidor iniciado:", "").strip()
            elif line.startswith("Input:"):
                lista_inputs.append(line.replace("Input:", "").strip())
            elif line.startswith("Código de salida:"):
                lista_salidas.append(line.replace("Código de salida:", "").strip())
            elif line.startswith("Conexión cerrada:"):
                hora_fin = line.replace("Conexión cerrada:", "").strip()
except FileNotFoundError:
    print("No se encontró el archivo de log:", LOG_FILE)
    exit(1)

if len(lista_inputs) != len(lista_salidas):
    print("¡Atención! El número de inputs y salidas no coincide.")
    exit(1)

resultados = list(zip(lista_inputs, lista_salidas))

# Parsear fecha y hora de inicio
if hora_inicio:
    try:
        fecha_i, tiempo_i = hora_inicio.split(" ")
        dt_i = datetime.strptime(fecha_i, "%d/%m/%Y")
        fecha_inicio = dt_i.strftime("%Y-%m-%d")
        hora_inicio_ = tiempo_i
    except ValueError:
        print("Error al procesar la fecha/hora de inicio.")
        exit(1)
else:
    fecha_inicio, hora_inicio_ = (None, None)

# Parsear fecha y hora de fin
if hora_fin:
    try:
        fecha_f, tiempo_f = hora_fin.split(" ")
        dt_f = datetime.strptime(fecha_f, "%d/%m/%Y")
        fecha_fin = dt_f.strftime("%Y-%m-%d")
        hora_fin_ = tiempo_f
    except ValueError:
        print("Error al procesar la fecha/hora de fin.")
        exit(1)
else:
    fecha_fin, hora_fin_ = (None, None)

# Conectar a MySQL usando la función importada
conn = get_connection()
if conn is None:
    exit(1)

cursor = conn.cursor()

insert_query = """
INSERT INTO fuzzing 
    (session_id, programa, input, exit_code, fecha_inicio, hora_inicio, fecha_fin, hora_fin)
VALUES 
    (%s, %s, %s, %s, %s, %s, %s, %s)
"""

for inp, out in resultados:
    data = (session_id, programa, inp, out, fecha_inicio, hora_inicio_, fecha_fin, hora_fin_)
    try:
        cursor.execute(insert_query, data)
    except Exception as err:
        print("Error al insertar datos:", err)

conn.commit()
cursor.close()
conn.close()
