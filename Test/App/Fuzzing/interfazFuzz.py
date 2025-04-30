#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import threading
import subprocess
import os
import shutil
import signal
import time
from config import root, get_selected_device, get_program_name

# Variables globales para almacenar hilos y procesos
server_thread = None
fuzzer_thread = None

server_process = None
fuzzer_process = None

# Crear carpeta Logs si no existe
LOG_DIR = os.path.expanduser("~/Documents/Versions/Test/App/Fuzzing/Logs")
os.makedirs(LOG_DIR, exist_ok=True)

def obtener_informacion():
    sudo_password = simpledialog.askstring("Contraseña sudo", "Introduce tu contraseña del PC:", show='*')
    if not sudo_password:
        messagebox.showerror("Error", "Contraseña no proporcionada.")
        return False

    base_dir = os.path.dirname(os.path.abspath(__file__))
    fuzzing_dir = os.path.abspath(os.path.join(base_dir, '..', 'Fuzzing'))
    inputs_dir = os.path.join(fuzzing_dir, "inputs")
    output_dir = os.path.join(fuzzing_dir, "outputs")
    
    os.makedirs(inputs_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    messagebox.showinfo("Fuzzing", "Selecciona un archivo TXT para inputs.")
    input_file_path = filedialog.askopenfilename(
        title="Selecciona un archivo TXT para inputs",
        filetypes=[("Text files", "*.txt")]
    )
    
    if not input_file_path:
        messagebox.showerror("Error", "Archivo de entrada no seleccionado. Debes seleccionar un archivo.")
        return False

    shutil.copy(input_file_path, inputs_dir)
    print(f"DEBUG: Archivo copiado a {inputs_dir}")

    # Iniciar hilos del servidor y fuzzer con un delay de 10 segundos para el fuzzer
    
    server_thread = threading.Thread(target=hilo_servidor, daemon=True)
    fuzzer_thread = threading.Thread(target=lambda: (time.sleep(30), hilo_fuzzer()), daemon=True)

    server_thread.start()
    fuzzer_thread.start()

    return True

# Ventana principal de Fuzzing
def open_fuzzing():
    root.withdraw()
    ventana_fuzz = tk.Toplevel()
    ventana_fuzz.title("Fuzzing")
    ventana_fuzz.geometry("300x250")

    btn_iniciar = tk.Button(ventana_fuzz, text="Iniciar", command=obtener_informacion)
    btn_iniciar.pack(pady=5)

    btn_parar = tk.Button(ventana_fuzz, text="Parar", command=parar_fuzzer)
    btn_parar.pack(pady=5)

    btn_analisis = tk.Button(ventana_fuzz, text="Análisis", command=realizar_analisis)
    btn_analisis.pack(pady=5)


    btn_volver = tk.Button(ventana_fuzz, text="Volver", command=lambda: [ventana_fuzz.destroy(), root.deiconify()])
    btn_volver.pack(pady=5)


# Solicitar contraseña y archivo antes de ejecutar procesos
def obtener_configuracion():
    return obtener_informacion()

def hilo_servidor():
    device = get_selected_device()
    program_name = get_program_name()
    if not device or not program_name:
        messagebox.showerror("Error", "Falta información para ejecutar el servidor.")
        return

    remote_user = device.get("usuario")
    remote_ip = device.get("ip")
    remote_command = f"cd ~/Documents/Fuzzing && python3 servidor.py {program_name}"

    ssh_command = ["ssh", f"{remote_user}@{remote_ip}", remote_command]
    print("DEBUG: Ejecutando servidor remoto:", " ".join(ssh_command))

    global server_process
    server_process = subprocess.Popen(ssh_command)
    # No usamos wait() aquí para evitar bloquear la interfaz
    server_process.poll()  # Revisa si el proceso está activo

def hilo_fuzzer():
    global fuzzer_process, sudo_password

    base_dir = os.path.dirname(os.path.abspath(__file__))
    fuzzing_dir = os.path.abspath(os.path.join(base_dir, '..', 'Fuzzing'))

    # Detener cualquier proceso afl-fuzz existente
    print("Deteniendo procesos afl-fuzz anteriores...")
    subprocess.run("ps aux | grep afl-fuzz | awk '{print $2}' | xargs kill -9", shell=True)

    time.sleep(5)
    
    afl_command = (
        f"cd {fuzzing_dir} && "
        f"timeout 30m afl-fuzz -n -i inputs -o outputs -t 1000 -m none -- "
        "timeout 30m sh -c 'cat @@ | socat - TCP:172.16.124.103:1234'"
    )

    print("DEBUG: Ejecutando comando afl-fuzz:", afl_command)

    fuzzer_process = subprocess.Popen(afl_command, shell=True)
    # No usamos wait() aquí para evitar bloquear la interfaz
    fuzzer_process.poll()  # Revisa si el proceso está activo

def parar_fuzzer():
    global server_process, fuzzer_process

    # Detener el fuzzer si está activo
    if fuzzer_process and fuzzer_process.poll() is None:
        fuzzer_process.send_signal(signal.SIGINT)

    # Detener el servidor si está activo
    if server_process and server_process.poll() is None:
        server_process.send_signal(signal.SIGINT)

    device = get_selected_device()
    program_name = get_program_name()

    if not device or not program_name:
        messagebox.showerror("Error", "Falta información para transferir logs.")
        return

    remote_user = device.get("usuario")
    remote_ip = device.get("ip")

    remote_path = f"{remote_user}@{remote_ip}:~/Documents/Fuzzing/Logs/{program_name}_log.txt"
    local_path = os.path.join(LOG_DIR, f"{program_name}_log.txt")

    scp_command = ["scp", remote_path, local_path]
    print("DEBUG: Ejecutando comando scp:", " ".join(scp_command))

    result = subprocess.run(scp_command, capture_output=True)

    if result.returncode == 0:
        messagebox.showinfo("Fuzzing", f"Log '{program_name}_log.txt' copiado correctamente.")
    else:
        messagebox.showerror(
            "Error",
            f"Error copiando el archivo: {result.stderr.decode().strip()}"
        )

    # Matar cualquier proceso ejecutando python3 en la Raspberry Pi
    try:
        device = get_selected_device()
        remote_user = device.get("usuario")
        remote_ip = device.get("ip")

        # Usar SSH para ejecutar el kill en la Raspberry Pi
        ssh_command = [
            "ssh", f"{remote_user}@{remote_ip}",
            "kill -9 $(pgrep -f 'python3')"
        ]
        result = subprocess.run(ssh_command, text=True, capture_output=True)

        if result.returncode == 0:
            print("DEBUG: Procesos python3 detenidos correctamente en la Raspberry Pi.")
        else:
            print("DEBUG: No se encontraron procesos python3 en la Raspberry Pi o hubo un error.")
    except Exception as e:
        print(f"DEBUG: Error al intentar detener procesos python3 en la Raspberry Pi: {e}")

def realizar_analisis():
    program_name = get_program_name()
    log_file_name = f"{program_name}_log.txt"

    base_dir = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(base_dir, "Logs", log_file_name)
    procesar_logs_path = os.path.join(base_dir, "Logs", "procesarLogs.py")
    dashboard_path = os.path.join(base_dir, "Dashbord", "dash2.py")  

    if not os.path.exists(log_path):
        messagebox.showerror("Error", f"No se encontró el archivo de log: {log_file_name}")
        return

    session_id = simpledialog.askinteger("Sesión", "Introduce el número de la sesión:")
    if session_id is None:
        messagebox.showwarning("Cancelado", "El análisis fue cancelado.")
        return

    try:
        subprocess.run(
            ["python3", procesar_logs_path, log_path, program_name, str(session_id)],
            check=True
        )
        messagebox.showinfo("Análisis", f"Análisis del log '{log_file_name}' completado correctamente.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error al ejecutar el análisis:\n{e}")
        return

    
    try:
        subprocess.Popen(["python3", dashboard_path, program_name, str(session_id)])
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo lanzar el dashboard:\n{e}")