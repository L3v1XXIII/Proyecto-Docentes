from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

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
    administrador = models.ForeignKey(Administrador, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    matricula = models.CharField(max_length=10)
    CURP = models.CharField(max_length=18)
    RFC = models.CharField(max_length=13)
    comprobante_domicilio = models.FileField(upload_to='comprobantes_domicilio/', null=True, blank=True)
    titulo = models.FileField(upload_to='titulos/', null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': 'docente'})

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
    dia = models.CharField(max_length=20)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.dia} {self.hora_inicio} - {self.hora_fin}"

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
