#!/bin/bash

REMOTE_USUARIO="markel"
REMOTE_IP="172.16.124.103"
REMOTE_DIR="~/Documents/Fuzzing/Logs"
REMOTE_ARCHIVO="dasdsadasdawdawefeavfesdfa_log.txt"

DESTINO_DIR="${HOME}/Documents/Versions/Test/App/Fuzzing/Logs"

scp "${REMOTE_USUARIO}@${REMOTE_IP}:${REMOTE_DIR}/${REMOTE_ARCHIVO}" "${DESTINO_DIR}/"

if [ $? -eq 0 ]; then
    echo "Archivo copiado exitosamente a ${DESTINO_DIR}/${REMOTE_ARCHIVO}"
else
    echo "Error durante la copia del archivo."
fi
