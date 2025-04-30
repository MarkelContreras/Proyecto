#!/usr/bin/env python3
import sys
import os
import subprocess
import socket
import codecs
import datetime

# Verificar que se pasó un argumento
if len(sys.argv) < 2:
    print("Uso: python3 logical.py <nombre>")
    sys.exit(1)

# El parámetro define el "nombre" base para el binario y el log
param = sys.argv[1]

# Crear carpeta Logs si no existe
LOG_DIR = "Logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Se asignan BINARIO y LOG_FILE basándose en el parámetro recibido
BINARIO = f"./{param}"
LOG_FILE = os.path.join(LOG_DIR, f"{param}_log.txt")

print("BINARIO configurado como:", BINARIO)
print("LOG_FILE configurado como:", LOG_FILE)

def ejecutar_binario(input_data):
    try:
        proceso = subprocess.run(
            [BINARIO],
            input=input_data,  # datos en bruto (bytes)
            capture_output=True,
            timeout=5
        )
        if proceso.returncode < 0:
            return -proceso.returncode
        else:
            return proceso.returncode
    except subprocess.TimeoutExpired:
        return 124  # Código de salida para timeout
    except Exception as e:
        print(f"Error al ejecutar el binario: {e}", file=sys.stderr)
        return 125  # Código de salida para errores internos

def guardar_log(input_data, exit_code):
    escaped_input = codecs.escape_encode(input_data)[0].decode('ascii')
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"Input: {escaped_input}\n")
        log.write(f"Código de salida: {exit_code}\n")
        log.write("--------------------------\n")

def log_connection_closed():
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"Conexión cerrada: {now}\n")
        log.write("--------------------------\n")

def start_server(host='0.0.0.0', port=1234):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Servidor escuchando en {host}:{port}...")
    
    try:
        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Conexión establecida con {client_address}")
            
            data = client_socket.recv(1024)
            if data:
                print(f"Input recibido: {data}")
                exit_code = ejecutar_binario(data)
                guardar_log(data, exit_code)
                client_socket.sendall(f"{exit_code}".encode('latin-1'))
            client_socket.close()
            log_connection_closed()
    
    except KeyboardInterrupt:
        print("Servidor detenido.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    # Limpiar el archivo de log al iniciar
    open(LOG_FILE, "wb").close()
    inicio = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"Servidor iniciado: {inicio}\n")
        log.write("--------------------------\n")
    
    start_server()