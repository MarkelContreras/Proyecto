#!/usr/bin/env python3
import tkinter as tk
import os


# Variable global: la ventana principal
root = tk.Tk()
root.title("Aplicación Principal")
root.geometry("300x200")

selected_device = None
selected_file = None

def set_selected_device(dev_info: dict):
    global selected_device
    selected_device = dev_info
    print("DEBUG: selected_device actualizado:", selected_device)

def get_selected_device():
    return selected_device

def set_selected_file(file_path: str):
    global selected_file
    selected_file = file_path
    print("DEBUG: selected_file actualizado:", selected_file)

def get_selected_file():
    return selected_file

def get_program_name():
    """Retorna el nombre del programa sin extensión basado en selected_file."""
    if selected_file:
        return os.path.splitext(os.path.basename(selected_file))[0]
    return None