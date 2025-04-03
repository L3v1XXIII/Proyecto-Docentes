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
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("El nombre de usuario debe ser proporcionado")

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        return self.create_user(username=username, password=password, **extra_fields)


# Custom User model
class User(AbstractUser):
    ROLE_CHOICES = (
        ('superadmin', 'Super Administrator'),
        ('admin', 'Administrator'),
        ('docente', 'Docente'),
    )

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = CustomUserManager()

    def __str__(self):
        return self.username




# Modelo de Carrera
class Carrera(models.Model):
    nombre = models.CharField(max_length=100)
    clave = models.CharField(max_length=10, unique=True)
    horas_semanales = models.IntegerField()

    def __str__(self):
        return self.nombre

# Administrador
class Administrador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': 'admin'})
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    clave = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=15)
    carreras = models.ManyToManyField('Carrera', blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.user:
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            user = User.objects.create_user(
                username=self.clave,
                email=self.email,
                password=password,
                role='admin',
                is_active=True
            )
            self.user = user

            send_mail(
                'Acceso al Sistema de Gestión de Horarios',
                f'Hola {self.nombre},\n\nTu cuenta ha sido creada.\n\nUsuario: {self.clave}\nContraseña: {password}\n\nPor favor cambia tu contraseña después de iniciar sesión.',
                'admin@tusistema.com',
                [self.email],
                fail_silently=True,
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

# Modelo para Periodo
class Periodo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

# Docente
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
    carrera = models.ForeignKey('Carrera', on_delete=models.SET_NULL, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': 'docente'})

    def save(self, *args, **kwargs):
        if not self.user:
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            user = User.objects.create_user(
                username=self.matricula,
                email=self.email,
                password=password,
                role='docente',
                is_active=True
            )
            self.user = user

            send_mail(
                'Acceso al Sistema de Gestión de Horarios',
                f'Hola {self.nombre},\n\nTu cuenta ha sido creada.\n\nUsuario: {self.matricula}\nContraseña: {password}\n\nPor favor cambia tu contraseña después de iniciar sesión.',
                'admin@tusistema.com',
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
    Grupo = models.ForeignKey('Grupo', on_delete=models.SET_NULL, null=True, blank=True)
    visible_para_todos = models.BooleanField(default=False)  
    
    def __str__(self):
        return self.nombre

# Modelo para Grupo
class Grupo(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


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

# Horario de Asignatura
class HorarioAsignatura(models.Model):
    DIAS_CHOICES = [
        ('lunes', 'Lunes'),
        ('martes', 'Martes'),
        ('miercoles', 'Miércoles'),
        ('jueves', 'Jueves'),
        ('viernes', 'Viernes'),
        ('sabado', 'Sábado'),
    ]

    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE, related_name='horarios')
    dia = models.CharField(max_length=10, choices=DIAS_CHOICES)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    class Meta:
        unique_together = ('asignatura', 'dia', 'hora_inicio')

    def clean(self):
        from django.core.exceptions import ValidationError

        # Verificar si hora_inicio y hora_fin no son None
        if self.hora_inicio is None or self.hora_fin is None:
            raise ValidationError("Las horas de inicio y fin deben ser válidas.")

        if self.hora_inicio >= self.hora_fin:
            raise ValidationError("La hora de inicio debe ser menor que la hora de fin.")

        duracion = (self.hora_fin.hour - self.hora_inicio.hour) * 60 + (self.hora_fin.minute - self.hora_inicio.minute)
        if duracion > 180:
            raise ValidationError("La duración total de la asignatura en un día no puede exceder 3 horas.")

        # Verificación de solapamientos
        solapamientos = HorarioAsignatura.objects.filter(
            asignatura__carrera=self.asignatura.carrera,
            dia=self.dia,
            hora_inicio__lt=self.hora_fin,
            hora_fin__gt=self.hora_inicio
        ).exclude(asignatura=self.asignatura)

        if solapamientos.exists():
            raise ValidationError("Ya existe una materia de la misma carrera en ese horario.")

        total_duracion = sum(
            (h.hora_fin.hour - h.hora_inicio.hour) * 60 + (h.hora_fin.minute - h.hora_inicio.minute)
            for h in HorarioAsignatura.objects.filter(asignatura=self.asignatura).exclude(pk=self.pk)
        ) + duracion

        if total_duracion > 180:
            raise ValidationError("La suma de todos los horarios de esta asignatura no puede exceder 3 horas semanales.")

    def __str__(self):
        return f"{self.asignatura.nombre} - {self.dia} ({self.hora_inicio} a {self.hora_fin})"

class DisponibilidadDocente(models.Model):
    docente = models.ForeignKey(Docente, on_delete=models.CASCADE, related_name='disponibilidades')
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    horarios = models.ManyToManyField(HorarioAsignatura)  # Relación ManyToMany para los horarios

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Guardamos el objeto DisponibilidadDocente primero
        # Agregamos las relaciones ManyToMany después de guardar el objeto principal
        self.horarios.set(self.horarios.all())  # Esto asegura que los horarios se asocien correctamente
        super().save(*args, **kwargs)  # Guardamos nuevamente para mantener la relación ManyToMany

class HorarioDocente(models.Model):
    docente = models.ForeignKey(Docente, on_delete=models.CASCADE, related_name='horarios_docente')
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    horarios = models.ManyToManyField(HorarioAsignatura)
    horas_semanales = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        # Recalcular las horas semanales cuando los horarios son asignados
        self.horas_semanales = sum(
            (horario.hora_fin.hour - horario.hora_inicio.hour) * 60 + (horario.hora_fin.minute - horario.hora_inicio.minute)
            for horario in self.horarios.all()
        ) // 60  # Convertir minutos a horas
        if self.horas_semanales > 18:
            raise ValueError("La cantidad total de horas semanales no puede exceder 18 horas.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.docente} - {self.asignatura.nombre}"
