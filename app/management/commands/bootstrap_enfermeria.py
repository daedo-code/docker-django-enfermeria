import secrets

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from app.models import Perfil, User


DEMO_ADMIN_USERNAME = 'demo_user'
DEMO_ADMIN_PASSWORD = 'demo_1234'
DEMO_ADMIN_RUT = 'DEMO-ADMIN-001'


class Command(BaseCommand):
    help = 'Crea o actualiza los perfiles base y un administrador inicial.'

    def add_arguments(self, parser):
        parser.add_argument('--username', default='admin', help='Nombre de usuario del administrador.')
        parser.add_argument('--password', help='Contrasena inicial del administrador.')
        parser.add_argument('--rut', default='ADMIN-001', help='RUT o identificador unico del administrador.')
        parser.add_argument('--nombre', default='Administrador')
        parser.add_argument('--apellido', default='Sistema')
        parser.add_argument('--direccion', default='No registrada')
        parser.add_argument('--reset-password', action='store_true', help='Actualiza la contrasena si el administrador ya existe.')
        parser.add_argument('--skip-migrate', action='store_true', help='No ejecuta migraciones antes de inicializar.')
        parser.add_argument('--with-demo-admin', action='store_true', help='Crea o actualiza el administrador de demostración.')

    def handle(self, *args, **options):
        if options['reset_password'] and not options['password']:
            raise CommandError('--reset-password requiere --password.')
        if not options['skip_migrate']:
            call_command('migrate', interactive=False, verbosity=0)

        admin_profile, _ = Perfil.objects.update_or_create(
            id='I01', defaults={'descripcion': 'Administradores'}
        )
        Perfil.objects.update_or_create(
            id='I02', defaults={'descripcion': 'Encargados'}
        )

        username = options['username']
        rut = options['rut']
        existing_by_username = User.objects.filter(username=username).first()
        existing_by_rut = User.objects.filter(rut=rut).first()
        if existing_by_username and existing_by_rut and existing_by_username.pk != existing_by_rut.pk:
            raise CommandError('El username y el RUT pertenecen a usuarios distintos.')

        user = existing_by_username or existing_by_rut
        generated_password = None
        if user is None:
            user = User(
                username=username,
                rut=rut,
                nombre=options['nombre'],
                apellido=options['apellido'],
                direccion=options['direccion'],
            )
            generated_password = options['password'] or secrets.token_urlsafe(18)
            user.set_password(generated_password)
            created = True
        else:
            created = False
            if user.rut != rut:
                raise CommandError('El administrador existente tiene un RUT distinto; no se cambia una clave primaria automaticamente.')
            user.username = username
            user.nombre = options['nombre']
            user.apellido = options['apellido']
            user.direccion = options['direccion']
            if options['reset_password']:
                user.set_password(options['password'])

        user.perfil = admin_profile
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()

        action = 'creado' if created else 'actualizado'
        self.stdout.write(self.style.SUCCESS(f'Perfiles listos y administrador {action}: {username}'))
        if generated_password:
            self.stdout.write(self.style.WARNING(f'Contrasena temporal de {username}: {generated_password}'))

        if options['with_demo_admin']:
            demo_created = self._create_or_update_demo_admin(admin_profile)
            demo_action = 'creado' if demo_created else 'actualizado'
            self.stdout.write(self.style.SUCCESS(
                f'Administrador de demostración {demo_action}: {DEMO_ADMIN_USERNAME}'
            ))

    def _create_or_update_demo_admin(self, admin_profile):
        existing_by_username = User.objects.filter(username=DEMO_ADMIN_USERNAME).first()
        existing_by_rut = User.objects.filter(rut=DEMO_ADMIN_RUT).first()
        if existing_by_username and existing_by_rut and existing_by_username.pk != existing_by_rut.pk:
            raise CommandError(
                'El username y el RUT del administrador de demostración pertenecen a usuarios distintos.'
            )

        user = existing_by_username or existing_by_rut
        if user is None:
            user = User(rut=DEMO_ADMIN_RUT)
            created = True
        else:
            created = False
            if user.rut != DEMO_ADMIN_RUT:
                raise CommandError(
                    'El administrador de demostración existente tiene un RUT distinto; no se cambia una clave primaria automáticamente.'
                )

        user.username = DEMO_ADMIN_USERNAME
        user.nombre = 'Administrador'
        user.apellido = 'Demostración'
        user.direccion = 'Cuenta de demostración'
        user.perfil = admin_profile
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(DEMO_ADMIN_PASSWORD)
        user.save()
        return created
