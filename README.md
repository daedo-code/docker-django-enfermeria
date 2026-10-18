# Sistema de Enfermeria

Aplicacion Django para gestionar pacientes, atenciones y encargados.

## Requisitos

- Python 3.11 o superior
- Docker Desktop con Docker Compose
- Un entorno virtual de Python con las dependencias de `requirements.txt`

## Inicio rapido

En Windows, activa el entorno virtual:

```cmd
.venv\Scripts\activate
```

Inicia MySQL:

```cmd
docker compose up -d
```

Comprueba que el contenedor este disponible:

```cmd
docker compose ps
```

Inicia la aplicacion:

```cmd
python manage.py runserver
```

Abre `http://127.0.0.1:8000/` en el navegador.

## Configuracion local

El proyecto carga automaticamente el archivo local `.env` mediante `django-environ`. Este contiene secretos y credenciales de MySQL, por lo que no debe subirse al repositorio. Las variables definidas en el sistema operativo o en el entorno de ejecucion tienen prioridad sobre los valores de `.env`.

Para configurar otra instalacion, crea `.env` desde `.env.example` y reemplaza todos los valores de ejemplo por secretos propios antes de iniciar Docker.

Variables principales:

```text
DJANGO_SECRET_KEY
DJANGO_DEBUG
DJANGO_ALLOWED_HOSTS
DJANGO_DB_USER
DJANGO_DB_PASSWORD
MYSQL_ROOT_PASSWORD
MYSQL_DATABASE
MYSQL_USER
MYSQL_PASSWORD
MYSQL_HOST
MYSQL_PORT
```

## Perfiles y administrador

El comando siguiente aplica migraciones y garantiza los perfiles base:

- `I01`: Administradores
- `I02`: Encargados

Tambien crea el usuario administrador `admin` si aun no existe:

```cmd
python manage.py bootstrap_enfermeria
```

Al crear un administrador por primera vez, el comando imprime una contrasena temporal. Guardala antes de cerrar la consola.

Para elegir la contrasena y el RUT:

```cmd
python manage.py bootstrap_enfermeria --password "UnaClaveSegura" --rut "ADMIN-001"
```

Para restablecer la contrasena de `admin`:

```cmd
python manage.py bootstrap_enfermeria --reset-password --password "NuevaClaveSegura"
```

## Datos de demostracion

El comando crea cinco encargados, cinco pacientes y cinco atenciones ficticias con datos clinicos coherentes:

```cmd
python manage.py seed_datos_prueba
```

Para eliminar y recrear exclusivamente los datos de demostracion:

```cmd
python manage.py seed_datos_prueba --clear
```

Los encargados demo usan los usuarios `demo_encargado_01` a `demo_encargado_05` y la contrasena:

```text
DemoSegura-2026
```

Los datos demo se identifican internamente por los usuarios `demo_encargado_*` y por el prefijo `DEMO:` en el procedimiento. El comando `--clear` tambien elimina los datos de prueba creados por versiones anteriores del comando.

No uses las credenciales ni datos de demostracion en produccion.

## Migraciones

El comando de inicializacion ya ejecuta migraciones. Si necesitas hacerlo manualmente:

```cmd
python manage.py migrate
```

Para comprobar que los modelos y migraciones estan sincronizados:

```cmd
python manage.py makemigrations --check
```

## Pruebas

Ejecuta la suite automatizada con:

```cmd
python manage.py test
```

## Detener servicios

Para detener MySQL sin borrar los datos:

```cmd
docker compose down
```

Elimina el volumen de MySQL solo si quieres perder todos los datos locales:

```cmd
docker compose down -v
```

Despues de eliminar el volumen, inicia nuevamente MySQL y ejecuta `python manage.py bootstrap_enfermeria` para reconstruir perfiles y administrador.
