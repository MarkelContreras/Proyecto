#!/bin/bash
# Uso: ./compilar_y_enviar.sh <32|64> <remote_ip> <remote_user> <ruta_al_archivo_fuente>
# Ejemplo: ./compilar_y_enviar.sh 64 172.16.124.103 markel /ruta/al/archivo/fuzzingProgram.c

# Verificar que se han pasado 4 parámetros
if [ "$#" -ne 4 ]; then
  echo "Uso: $0 <32|64> <remote_ip> <remote_user> <ruta_al_archivo_fuente>"
  exit 1
fi

ARCH="$1"
REMOTE_IP="$2"
REMOTE_USER="$3"
SOURCE_FILE="$4"

# Seleccionar el compilador según el parámetro de arquitectura
if [ "$ARCH" = "64" ]; then
  COMPILER="aarch64-linux-gnu-gcc"
  arch_name="ARM-64"
elif [ "$ARCH" = "32" ]; then
  COMPILER="arm-linux-gnueabihf-gcc"
  arch_name="ARM-32"
else
  echo "Arquitectura inválida: use '32' para ARM-32 o '64' para ARM-64."
  exit 1
fi

echo "Arquitectura seleccionada: $arch_name"
echo "REMOTE_IP: $REMOTE_IP, REMOTE_USER: $REMOTE_USER"

# Verificar que el archivo fuente existe
if [ ! -f "$SOURCE_FILE" ]; then
  echo "Error: No se encontró el archivo fuente '$SOURCE_FILE'."
  exit 1
fi

# Parte 1: Compilar el programa
echo "Compilando $(basename "$SOURCE_FILE") para $arch_name..."
$COMPILER -o fuzzingProgram "$SOURCE_FILE"
if [ $? -eq 0 ]; then
  echo "Compilación exitosa: 'fuzzingProgram' se ha creado."
else
  echo "Error al compilar '$(basename "$SOURCE_FILE")'."
  exit 1
fi

# Parte 2: Enviar el ejecutable vía SSH
FILE="fuzzingProgram"
if [ ! -f "$FILE" ]; then
    echo "Error: El archivo '$FILE' no se encuentra en el directorio actual."
    exit 1
fi

# Definir la carpeta remota: /home/<REMOTE_USER>/Documents/Fuzzing
REMOTE_DIR="/home/${REMOTE_USER}/Documents/Fuzzing"
echo "DIRECTORIO REMOTO: $REMOTE_DIR"

# Crear la carpeta remota si no existe (a través de SSH)
ssh ${REMOTE_USER}@${REMOTE_IP} "mkdir -p ${REMOTE_DIR}" || { 
    echo "Error al crear el directorio remoto $REMOTE_DIR en ${REMOTE_IP}"; 
    exit 1; 
}

# Enviar el archivo mediante SCP
echo "Enviando '$FILE' a ${REMOTE_USER}@${REMOTE_IP}:${REMOTE_DIR}..."
scp "$FILE" "${REMOTE_USER}@${REMOTE_IP}:${REMOTE_DIR}"
if [ $? -eq 0 ]; then
    echo "Archivo enviado correctamente."
else
    echo "Error al enviar el archivo."
fi
