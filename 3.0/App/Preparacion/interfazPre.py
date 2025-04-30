#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import subprocess
import os
import shutil
from config import root, get_selected_device, set_selected_file, get_selected_file
from config_db import get_database_name  

def open_preparacion():
    # Ocultar la ventana principal
    root.withdraw()
    
    ventana_pre = tk.Toplevel()
    ventana_pre.title("Preparación de Entornos")
    ventana_pre.geometry("300x200")
    
    # Botón "Ordenador"
    btn_ordenador = tk.Button(ventana_pre, text="Ordenador", command=preparar_ordenador)
    btn_ordenador.pack(pady=5)

    # Botón "Embebido"
    btn_embebido = tk.Button(ventana_pre, text="Embebido", command=preparar_embebido)
    btn_embebido.pack(pady=5)

    # Botón "Volver": cierra la ventana y muestra la principal
    btn_volver = tk.Button(ventana_pre, text="Volver", command=lambda: [ventana_pre.destroy(), root.deiconify()])
    btn_volver.pack(pady=5)


def preparar_ordenador():
    # Obtener el nombre de la base de datos
    database_name = get_database_name()

    # Ajustar la ruta del script
    script_path = os.path.join(os.path.dirname(__file__), "instalar_crear_dbs.sh")
    print("DEBUG: script_path =", script_path)

    if not os.path.exists(script_path):
        messagebox.showerror("Error", f"No se encontró el script en: {script_path}")
        return

    try:
        # Ejecutar el script pasando la base de datos como argumento
        result = subprocess.run(["bash", script_path, database_name], capture_output=True, text=True)
        
        print("DEBUG: returncode =", result.returncode)
        print("DEBUG: stdout =", result.stdout)
        print("DEBUG: stderr =", result.stderr)
        
        if result.returncode == 0:
            messagebox.showinfo("Bases de datos", f"Base de datos '{database_name}' creada correctamente.")
        else:
            stderr_lower = result.stderr.lower() if result.stderr else ""
            if "already exists" in stderr_lower or "ya existe" in stderr_lower:
                messagebox.showinfo("Bases de datos", f"La base de datos '{database_name}' ya existe.")
            else:
                messagebox.showerror(
                    "Error",
                    f"Error al ejecutar el script de creación de bases de datos:\n"
                    f"Return code: {result.returncode}\n"
                    f"stdout:\n{result.stdout}\n"
                    f"stderr:\n{result.stderr}"
                )
            return
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió una excepción al ejecutar el script:\n{e}")
        return
    
     # Abrir explorador de archivos
    ruta_archivo = filedialog.askopenfilename(title="Selecciona un archivo para copiar")
    if not ruta_archivo:
        messagebox.showinfo("Info", "No se seleccionó ningún archivo.")
        return

    # Copiar a carpeta Fuzzing/Programas
    carpeta_destino = os.path.join(os.path.dirname(__file__), "..", "Fuzzing", "Programas")
    if not os.path.exists(carpeta_destino):
        os.makedirs(carpeta_destino)

    nombre_original = os.path.basename(ruta_archivo)
    ruta_copiada = os.path.join(carpeta_destino, nombre_original)
    try:
        shutil.copy(ruta_archivo, ruta_copiada)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo copiar el archivo:\n{e}")
        return

    # Pedir un nuevo nombre
    nuevo_nombre = simpledialog.askstring("Renombrar archivo", "Introduce el nuevo nombre del programa (sin extensión):")
    if not nuevo_nombre:
        messagebox.showinfo("Info", "No se proporcionó un nuevo nombre. Se mantiene el nombre original.")
        set_selected_file(ruta_copiada)
        print("DEBUG: La ruta guardada en selected_file es:", get_selected_file())
        return

    _, extension = os.path.splitext(nombre_original)
    nuevo_nombre_con_ext = nuevo_nombre + extension
    ruta_nueva = os.path.join(carpeta_destino, nuevo_nombre_con_ext)
    try:
        os.rename(ruta_copiada, ruta_nueva)
        messagebox.showinfo("Renombrado", f"El archivo se ha renombrado a '{nuevo_nombre_con_ext}'.")
        set_selected_file(ruta_nueva)
        print("DEBUG: La ruta guardada en selected_file es:", get_selected_file())
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo renombrar el archivo:\n{e}")

def preparar_embebido():
    # Obtener la información del dispositivo y archivo seleccionados
    device = get_selected_device()
    file_path = get_selected_file()
    
    if device is None:
        messagebox.showerror("Error", "No se ha seleccionado ningún dispositivo.")
        return
    
    if file_path is None or not os.path.exists(file_path):
        messagebox.showerror("Error", "No se ha seleccionado un archivo válido.")
        return

    # Determinar la arquitectura
    arch = device.get("arquitectura", "").upper()
    if arch == "ARM-32":
        arch_param = "32"
        compiler = "arm-linux-gnueabihf-gcc"
    elif arch == "ARM-64":
        arch_param = "64"
        compiler = "aarch64-linux-gnu-gcc"
    else:
        messagebox.showerror("Error", f"Arquitectura no reconocida: {arch}")
        return

    remote_ip = device.get("ip")
    remote_user = device.get("usuario")
    if not remote_ip or not remote_user:
        messagebox.showerror("Error", "Faltan datos de conexión en el dispositivo seleccionado.")
        return

    # Definir carpeta remota
    remote_dir = f"/home/{remote_user}/Documents/Fuzzing"

    # Compilar el programa
    compile_command = [compiler, file_path]
    print("DEBUG: Compilando con comando:")
    print(" ".join(compile_command))
    try:
        subprocess.run(compile_command, check=True, capture_output=True, text=True)
    
        # Por defecto, gcc genera 'a.out'; renombramos para que tenga el nombre base del archivo fuente
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        if os.path.exists("a.out"):
            os.rename("a.out", base_name)
            compiled_binary = base_name
        else:
            compiled_binary = base_name

        print("Compilación exitosa: se ha creado", compiled_binary)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error al compilar:\n{e.stderr}")
        return
    
    # Crear directorio remoto vía SSH
    mkdir_command = ["ssh", f"{remote_user}@{remote_ip}", f"mkdir -p {remote_dir}"]
    print("DEBUG: Creando directorio remoto con:")
    print(" ".join(mkdir_command))
    try:
        subprocess.run(mkdir_command, check=True, capture_output=True, text=True)
        print("Directorio remoto creado o ya existente:", remote_dir)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error al crear el directorio remoto:\n{e.stderr}")
        return

    # Enviar el ejecutable compilado
    scp_command = ["scp", compiled_binary, f"{remote_user}@{remote_ip}:{remote_dir}"]
    print("DEBUG: Enviando ejecutable con:")
    print(" ".join(scp_command))
    try:
        subprocess.run(scp_command, check=True, capture_output=True, text=True)
        print("Ejecutable enviado correctamente.")
        # Borrar el compilado del ordenador local
        if os.path.exists(compiled_binary):
            os.remove(compiled_binary)
            print("DEBUG: Compilado borrado del ordenador.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error al enviar el ejecutable:\n{e.stderr}")
        return

    # Copiar también "servidor.py"
    SERVIDOR_FILE = os.path.join(os.path.dirname(__file__), "Embebido", "servidor.py")
    if not os.path.exists(SERVIDOR_FILE):
        messagebox.showerror("Error", f"No se encontró 'servidor.py' en: {SERVIDOR_FILE}")
        return

    scp_serv_command = ["scp", SERVIDOR_FILE, f"{remote_user}@{remote_ip}:{remote_dir}"]
    print("DEBUG: Enviando 'servidor.py' con:")
    print(" ".join(scp_serv_command))
    try:
        subprocess.run(scp_serv_command, check=True, capture_output=True, text=True)
        print("Archivo 'servidor.py' copiado correctamente.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error al copiar 'servidor.py':\n{e.stderr}")

if __name__ == "__main__":
    open_preparacion()
