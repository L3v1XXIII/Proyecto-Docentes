from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from datetime import timedelta, datetime, date
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
import random
import string
from django.core.exceptions import ValidationError

# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        return self.create_user(email, password, **extra_fields)

# User Model with Roles
class User(AbstractUser):
    ROLE_CHOICES = (
        ('superadmin', 'Super Administrator'),
        ('admin', 'Administrator'),
        ('docente', 'Docente'),
    )
    username = None
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_groups",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_permissions",
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


# Modelo de Carrera
class Carrera(models.Model):
    nombre = models.CharField(max_length=100)
    clave = models.CharField(max_length=10, unique=True)
    horas_semanales = models.IntegerField()

    def __str__(self):
        return self.nombre

# Modelo para Administrador
class Administrador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': 'admin'})
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    clave = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=15)
    carrera = models.ForeignKey(Carrera, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.user:
            # Generar una contraseña aleatoria de 10 caracteres
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

            # Crear un usuario con el mismo email
            user = User.objects.create(
                email=self.email,
                role='admin',
                password=make_password(password),  # Encriptar la contraseña
                is_active=True
            )

            # Asociar el usuario al administrador
            self.user = user

            # Opcional: Enviar email con la contraseña al usuario
            send_mail(
                'Acceso al Sistema de Gestión de Horarios',
                f'Hola {self.nombre},\n\nTu cuenta con credenciales de administrador ha sido creada.\n\nEmail: {self.email}\nContraseña: {password}\n\nPor favor cambia tu contraseña después de iniciar sesión.',
                'admin@tusistema.com',  # Cambia esto por el email del sistema
                [self.email],
                fail_silently=True,
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno} {self.apellido_materno}"

# Modelo para Periodo
class Periodo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

# Modelo de Docente
class Docente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    telefono = models.CharField(max_length=15)
    area = models.CharField(max_length=100)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    matricula = models.CharField(max_length=10)
    CURP = models.CharField(max_length=18)
    RFC = models.CharField(max_length=13)
    comprobante_domicilio = models.FileField(upload_to='comprobantes_domicilio/', null=True, blank=True)
    titulo = models.FileField(upload_to='titulos/', null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': 'docente'})

    def save(self, *args, **kwargs):
        if not self.user:
            # Generar una contraseña aleatoria de 10 caracteres
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

            # Crear un usuario con el mismo email
            user = User.objects.create(
                email=self.email,
                role='docente',
                password=make_password(password),  # Encriptar la contraseña
                is_active=True
            )

            # Asociar el usuario al docente
            self.user = user

            # Opcional: Enviar email con la contraseña al usuario
            send_mail(
                'Acceso al Sistema de Gestión de Horarios',
                f'Hola {self.nombre},\n\nTu cuenta ha sido creada.\n\nEmail: {self.email}\nContraseña: {password}\n\nPor favor cambia tu contraseña después de iniciar sesión.',
                'admin@tusistema.com',  # Cambia esto por el email del sistema
                [self.email],
                fail_silently=True,
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

# Modelo de Asignatura
class Asignatura(models.Model):
    nombre = models.CharField(max_length=100)
    clave = models.CharField(max_length=10, unique=True)
    matricula = models.CharField(max_length=10, unique=True)
    carrera = models.ForeignKey('Carrera', on_delete=models.CASCADE, null=True, blank=True) 
    periodo = models.ForeignKey('Periodo', on_delete=models.CASCADE, null=True, blank=True)  

    def __str__(self):
        return self.nombre

# Modelo para Grupo
class Grupo(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

#Recomendacion de horarios
class Disponibilidad(models.Model):
    DIAS_SEMANA = [
        ('Lunes', 'Lunes'),
        ('Martes', 'Martes'),
        ('Miércoles', 'Miércoles'),
        ('Jueves', 'Jueves'),
        ('Viernes', 'Viernes'),
        ('Sábado', 'Sábado'),
        ('Domingo', 'Domingo'),
    ]

    HORAS_DIA = [(f"{hora:02d}:00", f"{hora:02d}:00") for hora in range(7, 22)]  # De 07:00 a 21:00

    docente = models.ForeignKey(Docente, on_delete=models.CASCADE, related_name='disponibilidades')
    materia = models.ForeignKey('Asignatura', on_delete=models.CASCADE, null=True, blank=True) 
    dia = models.CharField(max_length=10, choices=DIAS_SEMANA)
    hora_inicio = models.CharField(max_length=5, choices=HORAS_DIA)
    hora_fin = models.CharField(max_length=5, choices=HORAS_DIA)

    def __str__(self):
        return f"{self.docente} - {self.dia} {self.hora_inicio}-{self.hora_fin}"

# Asignación de Docentes a Horarios y Asignaturas
class Horario(models.Model):
    DIAS_SEMANA = [
        ('Lunes', 'Lunes'),
        ('Martes', 'Martes'),
        ('Miércoles', 'Miércoles'),
        ('Jueves', 'Jueves'),
        ('Viernes', 'Viernes'),
        ('Sábado', 'Sábado'),
    ]
    HORAS = [
        ('07:00 - 08:30', '07:00 - 08:30'),
        ('08:30 - 10:00', '08:30 - 10:00'),
        ('10:00 - 11:30', '10:00 - 11:30'),
        ('11:30 - 13:00', '11:30 - 13:00'),
        ('13:00 - 14:30', '13:00 - 14:30'),
        ('14:30 - 16:00', '14:30 - 16:00'),
        ('16:00 - 17:30', '16:00 - 17:30'),
        ('17:30 - 19:00', '17:30 - 19:00'),
        ('19:00 - 20:30', '19:00 - 20:30'),
    ]
    
    dia = models.CharField(max_length=10, choices=DIAS_SEMANA)
    hora = models.CharField(max_length=15, choices=HORAS)
    docente = models.ForeignKey('Docente', on_delete=models.CASCADE, null=True, blank=True)
    materia = models.ForeignKey('Asignatura', on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        unique_together = ('dia', 'hora', 'docente')
    
    def __str__(self):
        return f"{self.materia} - {self.docente} ({self.dia} {self.hora})"
