from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
import uuid

# Create your models here.
    
# class Practicante(models.Model):
#     rut = models.CharField(primary_key=True, max_length=50)
#     nombre = models.CharField(max_length=50)
#     apellido = models.CharField(max_length=50)
#     direccion = models.CharField(max_length=50)
class Perfil(models.Model):
     id = models.CharField(primary_key=True, max_length=50)
     descripcion = models.CharField(max_length=50)

class User(AbstractUser):
    rut = models.CharField(primary_key=True, max_length=50)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    direccion = models.CharField(max_length=50)
    perfil = models.ForeignKey(Perfil, max_length=50, on_delete=models.PROTECT)

class Paciente(models.Model):
    rut = models.CharField(primary_key=True, max_length=50)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    direccion = models.CharField(max_length=50)
    habilitado = models.BooleanField(default=True)

class Atencion(models.Model):
    OPCIONES = (
        ('enfermedad', 'ENFERMEDAD'),
        ('accidente', 'ACCIDENTE'),
        ('estres', 'ESTRES')
        )
    id = models.CharField(primary_key=True, max_length=50, default=uuid.uuid4, editable=False)
    paciente = models.ForeignKey(Paciente, max_length=50, on_delete=models.PROTECT)
    fechaInicio = models.DateTimeField(auto_now_add=True)
    fechaTermino = models.DateTimeField(blank=True, null=True)
    sbp = models.IntegerField(validators=[MinValueValidator(50), MaxValueValidator(250)])
    dbp = models.IntegerField(validators=[MinValueValidator(30), MaxValueValidator(150)])
    pulso = models.IntegerField(validators=[MinValueValidator(20), MaxValueValidator(250)])
    temperatura = models.IntegerField(validators=[MinValueValidator(25), MaxValueValidator(45)])
    saturacion = models.IntegerField(validators=[MinValueValidator(50), MaxValueValidator(100)])
    procedimiento = models.TextField()
    razonIngreso = models.CharField(max_length=100, choices=OPCIONES)

    # ---------------- CAMPOS EN PROCESO DE EVALUACION ---------------------#
    # motivo_consulta = models.CharField(max_length=50, default='No motivo')
    practicante = models.ForeignKey(User, max_length=50, on_delete=models.PROTECT)
    terms = models.BooleanField(default=False)
    anulada = models.BooleanField(default=False)
    fechaAnulacion = models.DateTimeField(blank=True, null=True)
    anuladoPor = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name='atenciones_anuladas')
