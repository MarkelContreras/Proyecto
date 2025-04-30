import socket
import subprocess
import os
import sys
import codecs
import datetime

# Configuración
BINARIO = "./prueba"
LOG_FILE = "execution_log.txt"

def ejecutar_binario(input_data):
    try:
        proceso = subprocess.run(
            [BINARIO],
            input=input_data,  # Usar los datos en bruto (bytes)
            capture_output=True,
            timeout=5
        )
        
        # Si el proceso fue terminado por una señal (Unix)
        if proceso.returncode < 0:
            señal = -proceso.returncode
            return señal
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
    # Obtiene la fecha y hora actual en formato día/mes/año y hora:minutos
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"Conexión cerrada: {now}\n")
        log.write("--------------------------\n")

def start_server(host='0.0.0.0', port=1234):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Permitir reutilizar la dirección
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
                
                # Ejecutar el binario con el input recibido
                exit_code = ejecutar_binario(data)
                
                # Guardar el resultado en el archivo de log
                guardar_log(data, exit_code)
                
                # Enviar el código de salida al cliente
                client_socket.sendall(f"{exit_code}".encode('latin-1'))
            
            # Cerrar la conexión con el cliente
            client_socket.close()
            
            # Registrar la hora y fecha de cierre de la conexión
            log_connection_closed()
    
    except KeyboardInterrupt:
        print("Servidor detenido.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    # Limpiar el archivo de log al iniciar
    open(LOG_FILE, "wb").close()
    # Registrar la fecha y hora de inicio del servidor
    inicio = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"Servidor iniciado: {inicio}\n")
        log.write("--------------------------\n")
    
    start_server()
