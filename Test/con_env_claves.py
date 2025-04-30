#!/usr/bin/env python3
import os
import sys
import subprocess
import paramiko
import tkinter as tk
from tkinter import simpledialog, messagebox

def main():
    # Crear ventana principal (oculta)
    root = tk.Tk()
    root.withdraw()

    # Pedir datos de conexión mediante diálogos
    ip = simpledialog.askstring("Conexión SSH", "IP o Hostname:")
    if not ip:
        messagebox.showerror("Error", "No se proporcionó IP/Hostname.")
        sys.exit(1)
    usuario = simpledialog.askstring("Conexión SSH", "Usuario:")
    if not usuario:
        messagebox.showerror("Error", "No se proporcionó usuario.")
        sys.exit(1)
    password = simpledialog.askstring("Conexión SSH", "Contraseña:", show="*")
    if password is None:
        messagebox.showerror("Error", "No se proporcionó contraseña.")
        sys.exit(1)
    puerto = simpledialog.askinteger("Conexión SSH", "Puerto (presiona OK para usar 22):", initialvalue=22)
    if not puerto:
        puerto = 22

    # Intentar conexión SSH
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=ip, port=puerto, username=usuario, password=password, timeout=10)
        messagebox.showinfo("Conexión SSH", "Conexión realizada correctamente.")
    except Exception as e:
        messagebox.showerror("Conexión SSH", f"Error al conectar al dispositivo:\n{e}")
        sys.exit(1)

    # Directorio de claves SSH
    ssh_dir = os.path.join(os.path.expanduser("~"), ".ssh")
    if not os.path.exists(ssh_dir):
        os.makedirs(ssh_dir, mode=0o700)
    
    # Usar el nombre por defecto para las claves: id_ed25519 e id_ed25519.pub
    key_priv = os.path.join(ssh_dir, "id_ed25519")
    key_pub = key_priv + ".pub"
    
    # Generar las claves si no existen
    if os.path.exists(key_priv) and os.path.exists(key_pub):
        messagebox.showinfo("Claves SSH", "Las claves por defecto ya existen.")
    else:
        try:
            # Se genera el par de claves sin passphrase (-N "")
            subprocess.run(["ssh-keygen", "-t", "ed25519", "-f", key_priv, "-C", "fuzzingKeys", "-N", ""], check=True)
            messagebox.showinfo("Claves SSH", "Par de claves generado correctamente en ~/.ssh.")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Claves SSH", f"Error al generar las claves:\n{e}")
            ssh.close()
            sys.exit(1)
    
    # Leer la clave pública
    try:
        with open(key_pub, "r") as f:
            pub_key = f.read().strip()
    except Exception as e:
        messagebox.showerror("Claves SSH", f"Error al leer la clave pública:\n{e}")
        ssh.close()
        sys.exit(1)

    # Enviar la clave pública al dispositivo remoto
    # Se crea el directorio ~/.ssh en remoto, se ajustan permisos y se agrega la clave pública
    remote_cmd = (
        'mkdir -p ~/.ssh && chmod 700 ~/.ssh && '
        'echo "{}" >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys'
    ).format(pub_key.replace('"', '\\"'))
    
    try:
        stdin, stdout, stderr = ssh.exec_command(remote_cmd)
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            messagebox.showinfo("Clave Pública", "Clave pública enviada y agregada a ~/.ssh/authorized_keys correctamente.")
        else:
            err = stderr.read().decode().strip()
            messagebox.showerror("Clave Pública", f"Error al agregar la clave pública:\n{err}")
    except Exception as e:
        messagebox.showerror("Clave Pública", f"Error al ejecutar comando remoto:\n{e}")

    ssh.close()
    root.destroy()

if __name__ == "__main__":
    main()
