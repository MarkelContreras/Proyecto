#!/usr/bin/env python3
import sys
import mysql.connector
from datetime import datetime

if len(sys.argv) < 2:
    print("Uso: {} <archivo_log>".format(sys.argv[0]))
    exit(1)

LOG_FILE = sys.argv[1]

programa = os.path.basename(LOG_FILE).replace(".log", "")

lista_inputs = []
lista_salidas = []

hora_inicio = None
hora_fin = None

# Solicitar al usuario la sesión y el nombre del programa
try:
    session_id = int(input("Introduce el número de la sesión: "))
except ValueError:
    print("El ID de sesión debe ser un número entero.")
    exit(1)

# Procesar el archivo de log
try:
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("Servidor iniciado:"):
                if hora_inicio is None:
                    hora_inicio = line.replace("Servidor iniciado:", "").strip()
            elif line.startswith("Input:"):
                valor_input = line.replace("Input:", "").strip()
                lista_inputs.append(valor_input)
            elif line.startswith("Código de salida:"):
                valor_salida = line.replace("Código de salida:", "").strip()
                lista_salidas.append(valor_salida)
            elif line.startswith("Conexión cerrada:"):
                hora_fin = line.replace("Conexión cerrada:", "").strip()
except FileNotFoundError:
    print("No se encontró el archivo de log:", LOG_FILE)
    exit(1)

if len(lista_inputs) != len(lista_salidas):
    print("¡Atención! El número de inputs y salidas no coincide.")
    exit(1)

resultados = list(zip(lista_inputs, lista_salidas))

# Parseamos la fecha y la hora de inicio (dd/mm/yyyy hh:mm -> yyyy-mm-dd, hh:mm)
if hora_inicio:
    try:
        fecha_i, tiempo_i = hora_inicio.split(" ")
        dt_i = datetime.strptime(fecha_i, "%d/%m/%Y")
        fecha_inicio = dt_i.strftime("%Y-%m-%d")  # Formato para columnas DATE en MySQL
        hora_inicio_ = tiempo_i
    except ValueError:
        print("Error al procesar la fecha/hora de inicio.")
        exit(1)
else:
    fecha_inicio, hora_inicio_ = (None, None)

# Parseamos la fecha y la hora de fin (dd/mm/yyyy hh:mm -> yyyy-mm-dd, hh:mm)
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

# Conectar a la base de datos
try:
    conn = mysql.connector.connect(
        host="localhost",
        user="markel",
        password="markel",
        database="fuzzing_data"
    )
except mysql.connector.Error as err:
    print("Error al conectar a la base de datos:", err)
    exit(1)

cursor = conn.cursor()

insert_query = """
INSERT INTO fuzzing 
    (session_id, programa, input, exit_code, fecha_inicio, hora_inicio, fecha_fin, hora_fin)
VALUES 
    (%s, %s, %s, %s, %s, %s, %s, %s)
"""

# Insertar cada registro (cada par input/salida utiliza los mismos datos de sesión)
for inp, out in resultados:
    data = (session_id, programa, inp, out, fecha_inicio, hora_inicio_, fecha_fin, hora_fin_)
    try:
        cursor.execute(insert_query, data)
    except mysql.connector.Error as err:
        print("Error al insertar datos:", err)

conn.commit()
cursor.close()
conn.close()

print("Datos insertados correctamente en la base de datos.")
