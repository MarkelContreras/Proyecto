#!/bin/bash

# Verificar si se proporcionó un nombre de base de datos como argumento
if [ -z "$1" ]; then
  echo "Uso: $0 <nombre_de_la_base_de_datos>"
  exit 1
fi

# Variables de conexión
USER="root"
PASSWORD="markeladmin"
DATABASE="$1"  

# 1. Verificar si MariaDB/MySQL está instalado
if ! command -v mysql >/dev/null 2>&1 && ! command -v mariadb >/dev/null 2>&1; then
  echo "MariaDB/MySQL no está instalado. Procediendo a instalarlo..."
  sudo apt update
  sudo apt install mariadb-server -y
  # Opcional: Iniciar y habilitar el servicio
  sudo systemctl enable mariadb
  sudo systemctl start mariadb
else
  echo "MariaDB/MySQL ya está instalado."
fi

# 2. Crear la base de datos y las tablas
SQL_COMMANDS=$(cat <<EOF
CREATE DATABASE IF NOT EXISTS ${DATABASE};
USE ${DATABASE};

-- Tabla dispositivos
CREATE TABLE IF NOT EXISTS dispositivos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(255) NOT NULL,
  ip VARCHAR(50) NOT NULL,
  usuario VARCHAR(100) NOT NULL,
  password VARCHAR(100) NOT NULL,
  arquitectura VARCHAR(50)
);

-- Tabla fuzzing
CREATE TABLE IF NOT EXISTS fuzzing (
  id INT AUTO_INCREMENT PRIMARY KEY,
  session_id INT NOT NULL,
  programa VARCHAR(100) NOT NULL,
  input TEXT NOT NULL,
  exit_code INT NOT NULL,
  fecha_inicio DATE,
  hora_inicio TIME,
  fecha_fin DATE,
  hora_fin TIME
);
EOF
)

# 3. Ejecutar las sentencias en MySQL/MariaDB
mysql -u "${USER}" -p"${PASSWORD}" -e "${SQL_COMMANDS}"

if [ $? -eq 0 ]; then
  echo "Base de datos '${DATABASE}' y tablas creadas correctamente."
else
  echo "Ocurrió un error al crear la base de datos o las tablas."
fi
