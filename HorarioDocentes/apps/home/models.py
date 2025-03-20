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
    nombre = models.CharField(max_length=100, unique=True)
    codigo = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.nombre
    
    

# Modelo de Administrador
class Administrador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': 'admin'})
    carreras = models.ManyToManyField(Carrera)
    
    def __str__(self):
        return self.user.email

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
    codigo = models.CharField(max_length=20, unique=True)
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

# Modelo de Horarios
class Horario(models.Model):
    DIAS_SEMANA = [
        ('Lunes', 'Lunes'), ('Martes', 'Martes'), ('Miércoles', 'Miércoles'),
        ('Jueves', 'Jueves'), ('Viernes', 'Viernes'), ('Sábado', 'Sábado')
    ]
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    dia = models.CharField(max_length=20, choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        # 🔹 Calcular la duración en horas del nuevo horario
        duracion_nueva = (datetime.combine(date.today(), self.hora_fin) - datetime.combine(date.today(), self.hora_inicio)).total_seconds() / 3600

        # 🔹 Obtener la suma total de horas ya asignadas a la asignatura
        total_horas_existente = Horario.objects.filter(asignatura=self.asignatura).aggregate(
            total_horas=models.Sum(models.F('hora_fin') - models.F('hora_inicio'))
        )['total_horas']

        # 🔹 Convertir `total_horas_existente` a horas si no es `None`
        total_horas_existente = total_horas_existente.total_seconds() / 3600 if total_horas_existente else 0

        # 🔹 Validar que la asignatura no tenga más de 3 horas semanales
        if total_horas_existente + duracion_nueva > 3:
            raise ValueError("No se pueden asignar más de 3 horas semanales a esta asignatura.")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.asignatura.nombre} - {self.dia} {self.hora_inicio} - {self.hora_fin}"

#Recomendacion de horarios
class HorarioRecomendado(models.Model):
    docente = models.ForeignKey(Docente, on_delete=models.CASCADE)
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    horario = models.ForeignKey(Horario, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('docente', 'asignatura', 'horario')

    def save(self, *args, **kwargs):
        # 🔹 Calcular la duración en horas del nuevo horario
        duracion_nueva = (datetime.combine(date.today(), self.horario.hora_fin) - datetime.combine(date.today(), self.horario.hora_inicio)).total_seconds() / 3600

        # 🔹 Obtener la suma total de horas ya recomendadas por el docente
        total_horas_existente = HorarioRecomendado.objects.filter(docente=self.docente).aggregate(
            total_horas=models.Sum(models.F('horario__hora_fin') - models.F('horario__hora_inicio'))
        )['total_horas']

        total_horas_existente = total_horas_existente.total_seconds() / 3600 if total_horas_existente else 0

        # 🔹 Validar que el docente no exceda las 18 horas semanales
        if total_horas_existente + duracion_nueva > 18:
            raise ValueError("No puedes recomendar más de 18 horas semanales.")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Recomendado: {self.docente.email} - {self.asignatura.nombre} - {self.horario}"

# Asignación de Docentes a Horarios y Asignaturas
class Asignacion(models.Model):
    docente = models.ForeignKey(Docente, on_delete=models.CASCADE)
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    horario = models.ForeignKey(Horario, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('docente', 'asignatura', 'horario')

    def __str__(self):
        return f"{self.docente.email} - {self.asignatura.nombre} - {self.horario}"

# Reportes de Carga Académica
class ReporteCargaAcademica(models.Model):
    docente = models.ForeignKey(Docente, on_delete=models.CASCADE)
    total_horas = models.PositiveIntegerField()
    cuatrimestre = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.docente.email} - {self.total_horas}h en {self.cuatrimestre}"

class AsignacionMateria(models.Model):
    docente = models.ForeignKey(Docente, on_delete=models.CASCADE)
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE)  # 🔹 Se cambia Asignatura por Carrera
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    horario = models.ForeignKey(Horario, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('docente', 'asignatura', 'horario')

    def clean(self):
        """ Valida que el docente no tenga más de 18 horas semanales """
        total_horas_existente = AsignacionMateria.objects.filter(docente=self.docente).aggregate(
            total_horas=models.Sum(models.F('horario__hora_fin') - models.F('horario__hora_inicio'))
        )['total_horas']

        # Convertir `total_horas_existente` a horas si no es None
        total_horas_existente = total_horas_existente.total_seconds() / 3600 if total_horas_existente else 0

        # 🔹 Calcular duración del nuevo horario
        duracion_nueva = (self.horario.hora_fin.hour - self.horario.hora_inicio.hour) + \
                         (self.horario.hora_fin.minute - self.horario.hora_inicio.minute) / 60

        if total_horas_existente + duracion_nueva > 18:
            raise ValidationError("El docente no puede tener más de 18 horas semanales.")

    def save(self, *args, **kwargs):
        self.clean()  # Llamar a la validación antes de guardar
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.docente.email} - {self.asignatura.nombre} - {self.horario}"