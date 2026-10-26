# Hola Mundo con Docker Compose y MySQL

Aplicacion pequena en Python (Flask + Gunicorn) que muestra **Hola Mundo** y
guarda un contador de visitas en MySQL 8.4. El codigo esta en `src/`.

## Ejecutar

Requisitos: Git y Docker con Docker Compose v2 (por ejemplo, Docker Desktop).
No necesitas instalar Python ni MySQL en tu equipo.

```sh
git clone --branch juliorijo-practica-docker-compose https://github.com/juliorijo/practica-docker-compose.git
cd practica-docker-compose
cp .env.example .env
```

En PowerShell, usa `Copy-Item .env.example .env` en lugar de `cp`.
Edita `.env` y cambia las dos claves de ejemplo antes de iniciar. No subas
este archivo a GitHub. `MYSQL_USER` debe ser un usuario distinto de `root`.

```sh
docker compose config --quiet
docker compose up --build -d --wait
docker compose ps
```

Abre **http://localhost:8080**. Cada recarga incrementa el contador persistente.
Puedes cambiar el puerto con `APP_PORT` en `.env`. La web solo se publica en
la interfaz local y MySQL no expone puertos al equipo anfitrion.

```sh
curl http://localhost:8080/health
docker compose logs --tail=50 web db
docker compose down
```

`/health` devuelve `{"status":"ok"}` si MySQL responde; si falla, devuelve HTTP
503. En PowerShell puedes usar `curl.exe` para ejecutar el cliente curl.
Compose espera a que MySQL este listo antes de iniciar la web.

## Persistencia

El volumen `mysql_data` conserva los datos al detener o recrear los contenedores.
Para comprobarlo, anota el contador, ejecuta `docker compose down` y vuelve a
iniciar con `docker compose up -d --wait`: la siguiente visita debe incrementarlo.

`mysql/init.sql` se ejecuta solo al crear una base de datos vacia.
Cambiar las credenciales o el nombre de la BD en `.env` no modifica un volumen
ya inicializado: conserva sus valores o cambia los usuarios mediante SQL.
Para reiniciar la practica **eliminando todos los datos**:

```sh
docker compose down -v
docker compose up --build -d --wait
```

## Pruebas de la aplicacion (opcional, sin Docker)

Requiere Python 3.12. Las pruebas usan una conexion simulada; no sustituyen
la comprobacion con MySQL real mediante Compose.

```sh
python -m venv .venv
```

Activa el entorno con `.venv\Scripts\Activate.ps1` en PowerShell o
`source .venv/bin/activate` en Linux/macOS. Despues:

```sh
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

Repositorio: https://github.com/juliorijo/practica-docker-compose
