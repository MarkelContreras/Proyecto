#!/usr/bin/env python3
import os
import subprocess
from config import get_selected_device, get_selected_file

def launch_compilation():
    # Obtener información del dispositivo y del archivo seleccionado
    device = get_selected_device()
    file_path = get_selected_file()
    
    if device is None:
        print("Error: No se ha seleccionado ningún dispositivo.")
        return
    
    if file_path is None or not os.path.exists(file_path):
        print("Error: No se ha seleccionado un archivo válido.")
        return

    # Determinar la arquitectura y el compilador a usar
    arch = device.get("arquitectura", "").upper()
    if arch == "ARM-32":
        arch_param = "32"
        compiler = "arm-linux-gnueabihf-gcc"
    elif arch == "ARM-64":
        arch_param = "64"
        compiler = "aarch64-linux-gnu-gcc"
    else:
        print("Error: Arquitectura no reconocida:", arch)
        return

    remote_ip = device.get("ip")
    remote_user = device.get("usuario")
    if not remote_ip or not remote_user:
        print("Error: Faltan datos de conexión en el dispositivo seleccionado.")
        return

    # Definir la carpeta remota: /home/<remote_user>/Documents/Fuzzing
    remote_dir = f"/home/{remote_user}/Documents/Fuzzing"
    
    # Parte 1: Compilar el programa
    compiled_binary = "fuzzingProgram"
    compile_command = [compiler, "-o", compiled_binary, file_path]
    print("DEBUG: Compilando con comando:")
    print(" ".join(compile_command))
    try:
        subprocess.run(compile_command, check=True, capture_output=True, text=True)
        print("Compilación exitosa: se ha creado el ejecutable:", compiled_binary)
    except subprocess.CalledProcessError as e:
        print("Error al compilar el archivo fuente:")
        print(e.stderr)
        return

    # Parte 2: Crear el directorio remoto vía SSH
    mkdir_command = ["ssh", f"{remote_user}@{remote_ip}", f"mkdir -p {remote_dir}"]
    print("DEBUG: Ejecutando comando SSH para crear directorio:")
    print(" ".join(mkdir_command))
    try:
        subprocess.run(mkdir_command, check=True, capture_output=True, text=True)
        print("Directorio remoto creado (o ya existe):", remote_dir)
    except subprocess.CalledProcessError as e:
        print("Error al crear el directorio remoto:")
        print(e.stderr)
        return

    # Parte 3: Enviar el ejecutable compilado al directorio remoto con SCP
    scp_command = ["scp", compiled_binary, f"{remote_user}@{remote_ip}:{remote_dir}"]
    print("DEBUG: Ejecutando comando SCP para enviar el ejecutable:")
    print(" ".join(scp_command))
    try:
        subprocess.run(scp_command, check=True, capture_output=True, text=True)
        print("Ejecutable enviado correctamente.")
    except subprocess.CalledProcessError as e:
        print("Error al enviar el ejecutable:")
        print(e.stderr)
        return

    # Parte 4: Copiar también el archivo "servidor.py" al mismo directorio remoto
    SERVIDOR_FILE = "./servidor.py"
    if not os.path.exists(SERVIDOR_FILE):
        print("Error: No se encontró 'servidor.py' en el directorio actual.")
        return
    
    scp_serv_command = ["scp", SERVIDOR_FILE, f"{remote_user}@{remote_ip}:{remote_dir}"]
    print("DEBUG: Ejecutando comando SCP para 'servidor.py':")
    print(" ".join(scp_serv_command))
    try:
        subprocess.run(scp_serv_command, check=True, capture_output=True, text=True)
        print("Archivo 'servidor.py' copiado correctamente.")
    except subprocess.CalledProcessError as e:
        print("Error al copiar 'servidor.py':")
        print(e.stderr)

if __name__ == "__main__":
    launch_compilation()
