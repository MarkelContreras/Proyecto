import mysql.connector

def get_connection():
    """Establece y retorna una conexión a la base de datos local."""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",         # Usuario configurado en MariaDB
            password="markeladmin",  # Contraseña correspondiente
            database=get_database_name()  # Nombre de la base de datos dinámico
        )
        return conn
    except mysql.connector.Error as err:
        print("Error al conectar a la base de datos:", err)
        return None

def get_database_name():
    """Devuelve el nombre de la base de datos configurado en el archivo."""
    return "pruebafinal3"  # Modifica este valor si deseas otro nombre
