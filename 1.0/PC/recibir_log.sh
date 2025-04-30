#!/bin/bash

# Configuración de la conecxión rasberry + archivo y dirección que copiar
REMOTE_USUARIO="markel"
REMOTE_IP="172.16.124.103"
REMOTE_DIR="~/Desktop/Pruebas/Versions/1.0"
REMOTE_ARCHIVO="execution_log.txt"

# Donde los manda
DESTINO_DIR="${HOME}/Documents/Versions/1.0/datosFuzzing"

# Nuevo nombre
TIMESTAMP=$(date +"%d-%m-%Y_%H:%M")
NUEVO_NOMBRE="${TIMESTAMP}.txt"

# Copiar el archivo desde la Raspberry al Portátil
scp "${REMOTE_USUARIO}@${REMOTE_IP}:${REMOTE_DIR}/${REMOTE_ARCHIVO}" "${DESTINO_DIR}/${NUEVO_NOMBRE}"

# Comprobación
if [ $? -eq 0 ]; then
    echo "Archivo copiado exitosamente a ${DESTINO_DIR}/${NUEVO_NOMBRE}"
else
    echo "Error durante la copia del archivo."
fi
