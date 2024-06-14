import mysql.connector
import json
import os

# --- Set variables
MYSQL_DB_HOST = os.environ.get('MYSQL_DB_HOST')
MYSQL_DB_PORT = os.environ.get('MYSQL_DB_PORT')
MYSQL_DB_NAME = os.environ.get('MYSQL_DB_NAME')
MYSQL_DB_USER = os.environ.get('MYSQL_DB_USER')
MYSQL_DB_PASS = os.environ.get('MYSQL_DB_PASS')

def readDB(query):
    # Establecer la conexión con la base de datos
    conn = mysql.connector.connect(
        host=MYSQL_DB_HOST,
        port=MYSQL_DB_PORT,
        database=MYSQL_DB_NAME,
        user=MYSQL_DB_USER,
        password=MYSQL_DB_PASS
    )

    # Crear un cursor para ejecutar consultas SQL
    cur = conn.cursor()

    # Ejecutar una consulta de lectura
    cur.execute(query)

    # Obtener los resultados de la consulta
    rows = cur.fetchall()

    # Mostrar los resultados
    # for row in rows:
    #     print(row)

    # Cerrar el cursor y la conexión
    cur.close()
    conn.close()

    return rows
