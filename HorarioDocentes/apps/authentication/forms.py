# -*- encoding: utf-8 -*-

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from apps.home.models import User, Docente, Asignatura, Carrera, Horario, Administrador, HorarioRecomendado, AsignacionMateria
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
import random
import string
from django.db import models 
from datetime import datetime, date

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
    nombre = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Nombre", "class": "form-control"})
    )
    apellido_paterno = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Apellido Paterno", "class": "form-control"})
    )
    apellido_materno = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Apellido Materno", "class": "form-control"})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "Correo Electrónico", "class": "form-control"})
    )
    telefono = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Teléfono", "class": "form-control"})
    )
    area = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Área", "class": "form-control"})
    )
    matricula = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Matrícula", "class": "form-control"})
    )
    CURP = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "CURP", "class": "form-control"})
    )
    RFC = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "RFC", "class": "form-control"})
    )
    comprobante_domicilio = forms.FileField(
        widget=forms.ClearableFileInput(attrs={"class": "form-control-file"}), required=False
    )
    titulo = forms.FileField(
        widget=forms.ClearableFileInput(attrs={"class": "form-control-file"}), required=False
    )

    class Meta:
        model = Docente
        fields = [
            "nombre", "apellido_paterno", "apellido_materno", "email", "telefono",
            "area", "matricula", "CURP", "RFC", "comprobante_domicilio", "titulo"
        ]

    
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
    carrera = forms.ModelChoiceField(
        queryset=Carrera.objects.all(),
        widget=forms.Select(attrs={"class": "form-control", "id": "carrera-select"})
    )
    
    asignatura = forms.ModelChoiceField(
        queryset=Asignatura.objects.none(),  # 🔹 Inicialmente vacío
        widget=forms.Select(attrs={"class": "form-control", "id": "asignatura-select"})
    )

    dia = forms.ChoiceField(
        choices=Horario.DIAS_SEMANA,
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
        fields = ["carrera", "asignatura", "dia", "hora_inicio", "hora_fin"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "carrera" in self.data:
            try:
                carrera_id = int(self.data.get("carrera"))
                self.fields["asignatura"].queryset = Asignatura.objects.filter(carrera_id=carrera_id)
            except (ValueError, TypeError):
                pass  # Si el ID no es válido, no hacer nada

        elif self.instance.pk:
            self.fields["asignatura"].queryset = Asignatura.objects.filter(carrera=self.instance.carrera)
    
class AdministradorForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(role="admin"),  # Filtra solo usuarios con rol de administrador
        widget=forms.Select(attrs={"class": "form-control"})
    )
    carreras = forms.ModelMultipleChoiceField(
        queryset=Carrera.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "form-control"}),
        required=True,
        help_text="Selecciona las carreras que administrará este usuario."
    )

    class Meta:
        model = Administrador
        fields = ["user", "carreras"]

    def clean(self):
        cleaned_data = super().clean()
        carreras = cleaned_data.get("carreras")
        
        if carreras.exists():
            for carrera in carreras:
                if Administrador.objects.filter(carreras=carrera).exclude(user=self.instance.user).exists():
                    raise forms.ValidationError(f"La carrera {carrera.nombre} ya tiene un administrador asignado.")
        
        return cleaned_data

class CambiarContraseñaForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Contraseña Actual",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Contraseña actual"})
    )
    new_password1 = forms.CharField(
        label="Nueva Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Nueva contraseña"})
    )
    new_password2 = forms.CharField(
        label="Confirmar Nueva Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirmar nueva contraseña"})
    )

class HorarioRecomendadoForm(forms.ModelForm):
    asignatura = forms.ModelChoiceField(
        queryset=Asignatura.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    horario = forms.ModelChoiceField(
        queryset=Horario.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = HorarioRecomendado
        fields = ['asignatura', 'horario']

    def clean(self):
        cleaned_data = super().clean()
        docente = self.instance.docente  # Obtener el docente que envía el formulario
        horario = cleaned_data.get("horario")

        if docente and horario:
            # 🔹 Calcular la duración en horas del nuevo horario
            duracion_nueva = (datetime.combine(date.today(), horario.hora_fin) - datetime.combine(date.today(), horario.hora_inicio)).total_seconds() / 3600

            # 🔹 Obtener la suma total de horas ya recomendadas
            total_horas_existente = HorarioRecomendado.objects.filter(docente=docente).aggregate(
                total_horas=models.Sum(models.F('horario__hora_fin') - models.F('horario__hora_inicio'))
            )['total_horas']

            total_horas_existente = total_horas_existente.total_seconds() / 3600 if total_horas_existente else 0

            # 🔹 Validar que no se excedan las 18 horas semanales
            if total_horas_existente + duracion_nueva > 18:
                raise forms.ValidationError("No puedes recomendar más de 18 horas semanales.")

        return cleaned_data

class AsignacionMateriaForm(forms.ModelForm):
    carrera = forms.ModelChoiceField(
        queryset=Carrera.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    asignatura = forms.ModelChoiceField(
        queryset=Asignatura.objects.none(),  # 🔹 Se llenará dinámicamente con AJAX
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    horario = forms.ModelChoiceField(
        queryset=Horario.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = AsignacionMateria
        fields = ['carrera', 'asignatura', 'horario']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'carrera' in self.data:
            try:
                carrera_id = int(self.data.get('carrera'))
                self.fields['asignatura'].queryset = Asignatura.objects.filter(carrera_id=carrera_id)
            except (ValueError, TypeError):
                pass  # Manejo de error en caso de datos inválidos
        elif self.instance.pk:
            self.fields['asignatura'].queryset = self.instance.carrera.asignatura_set.all()