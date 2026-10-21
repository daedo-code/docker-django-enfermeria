# Cambios pendientes

## Antes de desplegar la tercera etapa

1. Verificar que MySQL esté disponible y revisar el estado de migraciones:

   ```sh
   .venv/bin/python manage.py showmigrations app
   ```

2. Aplicar la migración aditiva `app.0004_atencion_motivoanulacion_auditoriaatencion`:

   ```sh
   .venv/bin/python manage.py migrate
   ```

   Esta migración agrega un motivo nullable a las anulaciones y crea la tabla
   de auditoría. No elimina ni modifica atenciones existentes.

3. Ejecutar validación después de migrar:

   ```sh
   .venv/bin/python manage.py check
   .venv/bin/python manage.py test
   ```

## Configuración de producción

1. Definir una `DJANGO_SECRET_KEY` única, aleatoria y privada.
2. Configurar `DJANGO_DEBUG=false`.
3. Habilitar `DJANGO_SECURE_SSL_REDIRECT=true` solo si el sitio se publica por
   HTTPS.
4. Confirmar que `DJANGO_ALLOWED_HOSTS` contiene únicamente los dominios de
   despliegue autorizados.

## Mejoras futuras propuestas

1. Actualizar Django 4.2.4 a una versión actualmente soportada, con una etapa
   de compatibilidad y pruebas separada.
2. Corregir la configuración de despliegue de cPanel/Passenger, que aún
   contiene rutas y nombres de proyecto de ejemplo.
3. Incorporar paginación y filtros para las listas de pacientes y atenciones.
4. Evaluar una vista de solo lectura para consultar la auditoría clínica por
   administradores.
