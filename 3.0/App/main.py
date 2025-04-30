#!/usr/bin/env python3
from config import root
import tkinter as tk
from Preparacion import interfazPre
from Dispositivos import interfazDis
from Fuzzing import interfazFuzz
from config_db import get_connection

def main():
    
    btn_dispositivos = tk.Button(root, text="Dispositivos", command=interfazDis.open_dispositivos)
    btn_dispositivos.pack(pady=10)


    btn_preparacion = tk.Button(root, text="Preparación Entornos", command=interfazPre.open_preparacion)
    btn_preparacion.pack(pady=10)
    
    
    btn_fuzzing = tk.Button(root, text="Fuzzing", command=interfazFuzz.open_fuzzing)
    btn_fuzzing.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
