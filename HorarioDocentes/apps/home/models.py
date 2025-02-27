# -*- encoding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import  AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('super_admin', 'Super Admin'),
        ('admin', 'Admin'),
        ('docente', 'Docente'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="customuser_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="customuser_set",
        related_query_name="user",
    )

    def __str__(self):
        return self.username

class Carrera(models.Model):
    nombre = models.CharField(max_length=100)
    clave = models.CharField(max_length=10)
    horas_semanales = models.IntegerField()

    def __str__(self):
        return self.nombre

class Administrador(models.Model):
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    telefono = models.CharField(max_length=15)
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

class Docente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    telefono = models.CharField(max_length=15)
    area = models.CharField(max_length=100)
    administrador = models.ForeignKey(Administrador, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    matricula = models.CharField(max_length=10)
    CURP = models.CharField(max_length=18)
    RFC = models.CharField(max_length=13)
    comprobante_domicilio = models.CharField(max_length=255)
    titulo = models.CharField(max_length=255)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

class Disponibilidad(models.Model):
    docente = models.ForeignKey(Docente, on_delete=models.CASCADE)
    dia = models.CharField(max_length=10)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    def __str__(self):
        return f"{self.docente.nombre} - {self.dia}"

class Grupo(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Materia(models.Model):
    nombre = models.CharField(max_length=100)
    clave = models.CharField(max_length=10)
    matricula = models.CharField(max_length=10)

    def __str__(self):
        return self.nombre

class Horario(models.Model):
    docente = models.ForeignKey(Docente, on_delete=models.CASCADE)
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE)
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE)
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE)
    dia = models.CharField(max_length=10)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    def __str__(self):
        return f"{self.materia.nombre} - {self.dia} ({self.hora_inicio} - {self.hora_fin})"