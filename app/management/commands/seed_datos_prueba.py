from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from app.models import Atencion, Paciente, Perfil, User


DEMO_PROCEDURE_PREFIX = 'DEMO:'
LEGACY_PATIENT_PREFIX = 'TEST-PAC-'
LEGACY_USER_PREFIX = 'TEST-ENC-'
LEGACY_PROCEDURE_PREFIX = 'DATOS_PRUEBA:'
DEMO_PASSWORD = 'DemoSegura-2026'

DEMO_ENCARGADOS = (
    {'rut': '14.236.781-3', 'username': 'demo_encargado_01', 'nombre': 'Francisca', 'apellido': 'Herrera'},
    {'rut': '15.874.209-6', 'username': 'demo_encargado_02', 'nombre': 'Nicolas', 'apellido': 'Sepulveda'},
    {'rut': '16.492.735-8', 'username': 'demo_encargado_03', 'nombre': 'Antonia', 'apellido': 'Vargas'},
    {'rut': '17.305.948-1', 'username': 'demo_encargado_04', 'nombre': 'Sebastian', 'apellido': 'Fuentes'},
    {'rut': '18.761.420-5', 'username': 'demo_encargado_05', 'nombre': 'Constanza', 'apellido': 'Navarro'},
)

DEMO_PACIENTES = (
    {'rut': '12.345.678-5', 'nombre': 'Camila', 'apellido': 'Rojas', 'direccion': 'Av. Los Alerces 245, Santiago'},
    {'rut': '13.987.654-2', 'nombre': 'Javier', 'apellido': 'Morales', 'direccion': 'Pasaje El Molino 118, Providencia'},
    {'rut': '14.625.319-7', 'nombre': 'Daniela', 'apellido': 'Soto', 'direccion': 'Calle Los Canelos 530, Maipu'},
    {'rut': '15.418.762-9', 'nombre': 'Matias', 'apellido': 'Contreras', 'direccion': 'Av. Las Naciones 890, La Florida'},
    {'rut': '16.753.294-4', 'nombre': 'Valentina', 'apellido': 'Paredes', 'direccion': 'Pasaje Los Olivos 76, Nunoa'},
)


class Command(BaseCommand):
    help = 'Crea cinco encargados, pacientes y atenciones ficticias para desarrollo.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Elimina solo los registros marcados como datos de prueba antes de crearlos.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['clear']:
            self._clear_test_data()

        Perfil.objects.update_or_create(id='I01', defaults={'descripcion': 'Administradores'})
        encargado_profile, _ = Perfil.objects.update_or_create(
            id='I02', defaults={'descripcion': 'Encargados'}
        )

        now = timezone.now()
        motivos = ('enfermedad', 'accidente', 'estres', 'enfermedad', 'accidente')
        procedimientos = (
            'Control preventivo de signos vitales',
            'Evaluacion inicial por contusion leve',
            'Orientacion y control por cefalea tensional',
            'Control de parametros por cuadro respiratorio leve',
            'Seguimiento posterior a esguince de tobillo',
        )
        for index, (encargado_data, paciente_data) in enumerate(zip(DEMO_ENCARGADOS, DEMO_PACIENTES), start=1):
            encargado = self._upsert_encargado(encargado_data, encargado_profile)
            paciente = self._upsert_paciente(paciente_data)
            procedimiento = f'{DEMO_PROCEDURE_PREFIX} {procedimientos[index - 1]}'
            atencion, _ = Atencion.objects.update_or_create(
                paciente=paciente,
                procedimiento=procedimiento,
                defaults={
                    'practicante': encargado,
                    'sbp': 110 + index,
                    'dbp': 70 + index,
                    'pulso': 65 + index,
                    'temperatura': 36 + (index % 2),
                    'saturacion': 96 + (index % 3),
                    'razonIngreso': motivos[index - 1],
                    'terms': True,
                    'anulada': False,
                    'fechaAnulacion': None,
                    'anuladoPor': None,
                },
            )
            Atencion.objects.filter(pk=atencion.pk).update(
                fechaInicio=now - timedelta(days=index),
                fechaTermino=now - timedelta(days=index) + timedelta(minutes=30),
            )

        self.stdout.write(self.style.SUCCESS(
            'Datos de prueba listos: 5 encargados, 5 pacientes y 5 atenciones.'
        ))
        self.stdout.write(f'Contrasena de encargados demo: {DEMO_PASSWORD}')

    def _clear_test_data(self):
        demo_patient_ruts = [paciente['rut'] for paciente in DEMO_PACIENTES]
        demo_user_ruts = [encargado['rut'] for encargado in DEMO_ENCARGADOS]
        Atencion.objects.filter(
            Q(procedimiento__startswith=DEMO_PROCEDURE_PREFIX)
            | Q(procedimiento__startswith=LEGACY_PROCEDURE_PREFIX)
            | Q(paciente__rut__in=demo_patient_ruts)
            | Q(practicante__rut__in=demo_user_ruts)
            | Q(paciente__rut__startswith=LEGACY_PATIENT_PREFIX)
            | Q(practicante__rut__startswith=LEGACY_USER_PREFIX)
        ).delete()
        Paciente.objects.filter(
            Q(rut__in=demo_patient_ruts) | Q(rut__startswith=LEGACY_PATIENT_PREFIX)
        ).delete()
        User.objects.filter(
            Q(rut__in=demo_user_ruts) | Q(rut__startswith=LEGACY_USER_PREFIX)
        ).delete()

    def _upsert_encargado(self, data, perfil):
        encargado, _ = User.objects.update_or_create(
            rut=data['rut'],
            defaults={
                'username': data['username'],
                'nombre': data['nombre'],
                'apellido': data['apellido'],
                'direccion': 'Direccion de demostracion',
                'perfil': perfil,
                'is_active': True,
                'is_staff': False,
                'is_superuser': False,
            },
        )
        encargado.set_password(DEMO_PASSWORD)
        encargado.save(update_fields=['password'])
        return encargado

    def _upsert_paciente(self, data):
        return Paciente.objects.update_or_create(
            rut=data['rut'],
            defaults={
                'nombre': data['nombre'],
                'apellido': data['apellido'],
                'direccion': data['direccion'],
                'habilitado': True,
            },
        )[0]
