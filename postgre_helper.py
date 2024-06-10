import psycopg2,json
import os

# --- Set variables
POSTGRE_DB_HOST = os.environ.get('POSTGRE_DB_HOST')
POSTGRE_DB_PORT = os.environ.get('POSTGRE_DB_PORT')
POSTGRE_DB_NAME = os.environ.get('POSTGRE_DB_NAME')
POSTGRE_DB_USER = os.environ.get('POSTGRE_DB_USER')
POSTGRE_DB_PASS = os.environ.get('POSTGRE_DB_PASS')


def readDB(query):
    # Establecer la conexión con la base de datos
    conn = psycopg2.connect(
        database=POSTGRE_DB_NAME,
        user=POSTGRE_DB_USER,
        password=POSTGRE_DB_PASS,
        host=POSTGRE_DB_HOST,
        port=POSTGRE_DB_PORT
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