# Registro de cambios

## Pendiente de publicación

### Etapa 1: entorno y autenticación

- Se configuró `LOGIN_URL` para que las vistas protegidas redirijan al inicio
  de sesión del proyecto (`signin`).
- Se recreó el entorno virtual con CPython 3.12.15 y se instalaron las
  dependencias bloqueadas por el proyecto.
- `manage.py check`, `makemigrations --check --dry-run` y la suite de seis
  pruebas finalizaron correctamente con SQLite temporal, sin usar datos de
  MySQL.
- La consulta del estado aplicado de migraciones en MySQL queda pendiente:
  el servidor configurado en `localhost` no estaba disponible.

### Etapa 2: configuración y seguridad

- Se eliminaron del archivo de ejemplo las variables de root de MySQL y una
  variable no utilizada que contenía una credencial.
- En producción Django exige una clave secreta explícita y no inicia con
  valores de ejemplo o una clave conocida; en desarrollo usa una clave
  aleatoria efímera para mantener el arranque local.
- `DJANGO_DEBUG` es falso por defecto; el desarrollo local conserva la opción
  de habilitarlo explícitamente desde `.env`.
- Se actualizó la documentación de variables y de requisitos de Python.

### Etapa 3: protección de atenciones clínicas

- Los encargados pueden consultar todas las atenciones, pero solo crear y
  editar las propias mientras estén activas.
- Los administradores pueden editar cualquier atención activa y son los únicos
  autorizados para anularla.
- Las anulaciones ahora exigen un motivo, conservan el registro y bloquean toda
  edición posterior.
- Se añadió una auditoría separada para registrar creación, edición y
  anulación con actor, fecha, motivo y valores anteriores/nuevos.

### Etapa 4: limpieza de templates y rutas

- Se eliminaron templates sin referencias activas.
- Los enlaces y acciones internas de los templates activos ahora usan rutas
  nombradas con la etiqueta `{% url %}`.
- La anulación de atenciones ahora solicita el motivo mediante un modal,
  manteniendo la validación obligatoria del servidor.
