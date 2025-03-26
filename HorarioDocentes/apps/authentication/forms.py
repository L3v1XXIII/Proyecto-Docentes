# -*- encoding: utf-8 -*-

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from apps.home.models import User, Docente, Asignatura, Carrera, Horario, Administrador, Periodo, Grupo, Disponibilidad
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

    
# AsignaturaForm
class AsignaturaForm(forms.ModelForm):
    nombre = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Nombre de la asignatura", "class": "form-control"}))
    clave = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Clave", "class": "form-control"}))
    matricula = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Matrícula", "class": "form-control"}))
    carrera = forms.ModelChoiceField(queryset=Carrera.objects.all(), required=False, widget=forms.Select(attrs={"class": "form-control"}))
    periodo = forms.ModelChoiceField(queryset=Periodo.objects.all(), required=False, widget=forms.Select(attrs={"class": "form-control"}))

    class Meta:
        model = Asignatura
        fields = ["nombre", "clave", "matricula", "carrera", "periodo"]

# GrupoForm
class GrupoForm(forms.ModelForm):
    nombre = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Nombre del grupo", "class": "form-control"}))

    class Meta:
        model = Grupo
        fields = ["nombre"]

    
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

# HorarioForm
class HorarioForm(forms.ModelForm):
    dia = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Dia", "class": "form-control"}
        )
    )
    hora = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Hora", "class": "form-control"}
        )
    )
    docente = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Nombre del Docente", "class": "form-control"}
        )
    )
    materia = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Nombre de la Materia", "class": "form-control"}
        )
    )
    class Meta:
        model = Horario
        fields = ["dia", "hora", "docente", "materia"]
    
    # DisponibilidadForm
class DisponibilidadForm(forms.ModelForm):
    class Meta:
        model = Disponibilidad
        fields = ["docente", "materia", "dia", "hora_inicio", "hora_fin"]
        widgets = {
            "docente": forms.Select(attrs={"class": "form-control"}),
            "materia": forms.Select(attrs={"class": "form-control"}),
            "dia": forms.Select(attrs={"class": "form-control"}),
            "hora_inicio": forms.Select(attrs={"class": "form-control"}),
            "hora_fin": forms.Select(attrs={"class": "form-control"}),
        }
    

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
    
# AdministradorForm
class AdministradorForm(forms.ModelForm):
    nombre = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Nombre", "class": "form-control"}))
    apellido_paterno = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Apellido Paterno", "class": "form-control"}))
    apellido_materno = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Apellido Materno", "class": "form-control"}))
    clave = forms.CharField(required=False, widget=forms.TextInput(attrs={"placeholder": "Clave", "class": "form-control"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"placeholder": "Correo Electrónico", "class": "form-control"}))
    telefono = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Teléfono", "class": "form-control"}))
    carrera = forms.ModelChoiceField(queryset=Carrera.objects.all(), required=False, widget=forms.Select(attrs={"class": "form-control"}))

    class Meta:
        model = Administrador
        fields = ["nombre", "apellido_paterno", "apellido_materno", "clave", "email", "telefono", "carrera"]

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
