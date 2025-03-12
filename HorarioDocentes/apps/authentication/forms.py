# -*- encoding: utf-8 -*-

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from apps.home.models import User, Docente, Asignatura, Carrera, Horario, Administrador
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from datetime import datetime, date
from django.db import models
from django.db.models import Sum

class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.TextInput(attrs={"placeholder": "Correo electrónico", "class": "form-control", "name": "email"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Contraseña", "class": "form-control", "name": "password"})
    )

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        
        if email and password:
            self.user = authenticate(username=email, password=password)
            if not self.user:
                raise forms.ValidationError("Correo o contraseña incorrectos.")
        
        return self.cleaned_data

    def get_user(self):
        return self.user


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Nombre",
                "class": "form-control"
            }
        )
    )
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Apellido",
                "class": "form-control"
            }
        )
    )
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,  
        widget=forms.Select(
            attrs={
                "class": "form-control"
            }
        )
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control"
            }
        )
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Contraseña",
                "class": "form-control"
            }
        ))
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Confirmar Contraseña",
                "class": "form-control"
            }
        ))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'role', 'email')

class DocenteForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(role="docente"),  # Filtra solo usuarios con rol de docente
        widget=forms.Select(attrs={"class": "form-control"})
    )
    nombre = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Nombre", "class": "form-control"}
        )
    )
    apellido_paterno = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Apellido Paterno", "class": "form-control"}
        )
    )
    apellido_materno = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Apellido Materno", "class": "form-control"}
        )
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"placeholder": "Correo Electrónico", "class": "form-control"}
        )
    )
    telefono = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Teléfono", "class": "form-control"}
        )
    )
    area = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Área", "class": "form-control"}
        )
    )
    administrador = forms.ModelChoiceField(
        queryset=Administrador.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"})
    )
    matricula = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Matrícula", "class": "form-control"}
        )
    )
    CURP = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "CURP", "class": "form-control"}
        )
    )
    RFC = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "RFC", "class": "form-control"}
        )
    )
    comprobante_domicilio = forms.FileField(
        widget=forms.ClearableFileInput(
            attrs={"class": "form-control-file"}
        ),
        required=False
    )
    titulo = forms.FileField(
        widget=forms.ClearableFileInput(
            attrs={"class": "form-control-file"}
        ),
        required=False
    )

    class Meta:
        model = Docente
        fields = ["user", "nombre", "apellido_paterno", "apellido_materno", "email", "telefono", "area", "matricula", "CURP", "RFC", "comprobante_domicilio", "titulo", "administrador"]

class AsignaturaForm(forms.ModelForm):
    codigo = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Código de la asignatura", "class": "form-control"}
        )
    )
    nombre = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Nombre de la asignatura", "class": "form-control"}
        )
    )
    carrera = forms.ModelChoiceField(
        queryset=Carrera.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"})
    )
    
    class Meta:
        model = Asignatura
        fields = ["codigo", "nombre", "carrera"]
    
class CarreraForm(forms.ModelForm):
    codigo = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Código de la carrera", "class": "form-control"}
        )
    )
    nombre = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Nombre de la carrera", "class": "form-control"}
        )
    )
    
    class Meta:
        model = Carrera
        fields = ["codigo", "nombre"]

class HorarioForm(forms.ModelForm):
    asignatura = forms.ModelChoiceField(
        queryset=Asignatura.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"})
    )
    carrera = forms.ModelChoiceField(
        queryset=Carrera.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"})
    )
    dia = forms.ChoiceField(
        choices=[
            ('Lunes', 'Lunes'), ('Martes', 'Martes'), ('Miércoles', 'Miércoles'),
            ('Jueves', 'Jueves'), ('Viernes', 'Viernes'), ('Sábado', 'Sábado')
        ],
        widget=forms.Select(attrs={"class": "form-control"})
    )
    hora_inicio = forms.TimeField(
        widget=forms.TimeInput(attrs={"type": "time", "class": "form-control"})
    )
    hora_fin = forms.TimeField(
        widget=forms.TimeInput(attrs={"type": "time", "class": "form-control"})
    )

    class Meta:
        model = Horario
        fields = ["asignatura", "carrera", "dia", "hora_inicio", "hora_fin"]

    def clean(self):
        cleaned_data = super().clean()
        asignatura = cleaned_data.get("asignatura")
        hora_inicio = cleaned_data.get("hora_inicio")
        hora_fin = cleaned_data.get("hora_fin")

        if not asignatura or not hora_inicio or not hora_fin:
            return cleaned_data  # Evita validaciones si algún campo está vacío

        # 🔹 Convertimos `hora_inicio` y `hora_fin` a `datetime`
        base_date = date.today()
        hora_inicio_dt = datetime.combine(base_date, hora_inicio)
        hora_fin_dt = datetime.combine(base_date, hora_fin)

        # 🔹 Validar que la hora de fin es mayor a la de inicio
        if hora_fin_dt <= hora_inicio_dt:
            raise ValidationError("La hora de fin debe ser después de la hora de inicio.")

        # 🔹 Calcular la duración en horas del nuevo horario
        duracion_nueva = (hora_fin_dt - hora_inicio_dt).total_seconds() / 3600

        # 🔹 Obtener el total de horas de la asignatura
        total_horas_existente = Horario.objects.filter(asignatura=asignatura).aggregate(
            total_horas=Sum('hora_fin') - Sum('hora_inicio')
        )['total_horas']

        # 🔹 Convertir total_horas_existente a horas
        total_horas_existente = total_horas_existente.total_seconds() / 3600 if total_horas_existente else 0

        # 🔹 Verificar que no se excedan las 3 horas semanales
        if total_horas_existente + duracion_nueva > 3:
            raise ValidationError("No se pueden asignar más de 3 horas semanales a esta asignatura.")

        return cleaned_data