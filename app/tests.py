from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Atencion, Paciente, Perfil, User


class AccessControlTests(TestCase):
    def setUp(self):
        self.admin_profile = Perfil.objects.create(id='I01', descripcion='Administradores')
        self.encargado_profile = Perfil.objects.create(id='I02', descripcion='Encargados')
        self.admin = User.objects.create_user(
            username='admin', password='Strong-password-123', rut='1-9', nombre='Admin',
            apellido='Sistema', direccion='Direccion', perfil=self.admin_profile, is_staff=True,
            is_superuser=True,
        )
        self.encargado = User.objects.create_user(
            username='encargado', password='Strong-password-123', rut='2-7', nombre='Encargado',
            apellido='Uno', direccion='Direccion', perfil=self.encargado_profile,
        )
        self.paciente = Paciente.objects.create(rut='11.111.111-K', nombre='Paciente', apellido='Uno', direccion='Direccion')

    def test_private_pages_require_login(self):
        response = self.client.get(reverse('panel-paciente'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('signin'), response.url)

    def test_encargado_cannot_manage_accounts(self):
        self.client.force_login(self.encargado)
        response = self.client.get(reverse('panel-practicante'))
        self.assertEqual(response.status_code, 403)

    def test_atencion_requires_confirmation_and_assigns_allowed_encargado(self):
        self.client.force_login(self.encargado)
        url = reverse('panel-atencion-add', args=[self.paciente.rut])
        payload = {
            'sbp': 120,
            'dbp': 80,
            'pulso': 72,
            'temperatura': 37,
            'saturacion': 98,
            'procedimiento': 'Control general',
            'practicante': self.encargado.rut,
            'razonIngreso': 'enfermedad',
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Atencion.objects.count(), 0)

        response = self.client.post(url, {**payload, 'terms': 'on'})
        self.assertRedirects(response, reverse('panel-atencion'))
        atencion = Atencion.objects.get()
        self.assertTrue(atencion.terms)
        self.assertEqual(atencion.practicante, self.encargado)
        self.assertIsNotNone(atencion.fechaInicio)

    def test_admin_annuls_instead_of_deleting_atencion(self):
        atencion = Atencion.objects.create(
            paciente=self.paciente, practicante=self.encargado, sbp=120, dbp=80,
            pulso=72, temperatura=37, saturacion=98, procedimiento='Control',
            razonIngreso='enfermedad', terms=True,
        )
        self.client.force_login(self.admin)
        response = self.client.post(reverse('panel-atencion-anular', args=[atencion.id]))
        self.assertRedirects(response, reverse('panel-atencion'))
        atencion.refresh_from_db()
        self.assertTrue(atencion.anulada)
        self.assertEqual(atencion.anuladoPor, self.admin)


class BootstrapCommandTests(TestCase):
    def test_bootstrap_creates_profiles_and_admin(self):
        call_command(
            'bootstrap_enfermeria', '--username', 'root-admin', '--password', 'Strong-password-123',
            '--rut', 'ADMIN-1', verbosity=0,
        )
        admin = User.objects.get(username='root-admin')
        self.assertTrue(admin.is_superuser)
        self.assertEqual(admin.perfil_id, 'I01')
        self.assertEqual(Perfil.objects.get(pk='I02').descripcion, 'Encargados')


class SeedCommandTests(TestCase):
    def test_seed_creates_and_clears_only_test_data(self):
        real_patient = Paciente.objects.create(
            rut='REAL-001', nombre='Paciente', apellido='Real', direccion='Direccion real'
        )

        call_command('seed_datos_prueba')
        self.assertEqual(User.objects.filter(username__startswith='demo_encargado_').count(), 5)
        self.assertEqual(Paciente.objects.filter(nombre__in=['Camila', 'Javier', 'Daniela', 'Matias', 'Valentina']).count(), 5)
        self.assertEqual(Atencion.objects.filter(procedimiento__startswith='DEMO:').count(), 5)

        call_command('seed_datos_prueba', '--clear')
        self.assertTrue(Paciente.objects.filter(pk=real_patient.pk).exists())
        self.assertEqual(User.objects.filter(username__startswith='demo_encargado_').count(), 5)
        self.assertEqual(Paciente.objects.filter(nombre__in=['Camila', 'Javier', 'Daniela', 'Matias', 'Valentina']).count(), 5)
        self.assertEqual(Atencion.objects.filter(procedimiento__startswith='DEMO:').count(), 5)
