import os

import pymysql
from flask import Flask, render_template_string

app = Flask(__name__)

PAGE = """<!doctype html>
<html lang="es">
<head><meta charset="utf-8"><title>Hola Mundo</title></head>
<body>
  <h1>Hola Mundo</h1>
  <p>Conexion a MySQL correcta.</p>
  <p>Visitas guardadas en MySQL: <strong>{{ total }}</strong></p>
</body>
</html>
"""


def connect_db():
    return pymysql.connect(
        host=os.environ["MYSQL_HOST"],
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        database=os.environ["MYSQL_DATABASE"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5,
        read_timeout=5,
        write_timeout=5,
    )


@app.get("/")
def index():
    try:
        with connect_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE visitas SET total = total + 1 WHERE id = 1")
                cursor.execute("SELECT total FROM visitas WHERE id = 1")
                row = cursor.fetchone()
                if row is None:
                    app.logger.error("Falta el contador inicial en la tabla visitas")
                    return "La base de datos no esta inicializada correctamente.", 503
            connection.commit()
    except pymysql.MySQLError as error:
        app.logger.error("Error de MySQL al registrar una visita: %s", type(error).__name__)
        return "No se pudo acceder a MySQL. Consulta los logs del servicio.", 503

    return render_template_string(PAGE, total=row["total"])


@app.get("/health")
def health():
    try:
        with connect_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
    except pymysql.MySQLError as error:
        app.logger.error("Error de MySQL en health: %s", type(error).__name__)
        return {"status": "error"}, 503
    return {"status": "ok"}
