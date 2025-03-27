# -*- encoding: utf-8 -*-

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from apps.home.models import User, Docente, Asignatura, Carrera, Horario, Administrador, Periodo, Grupo, Disponibilidad
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
import re
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
        label="Nombre",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Nombre",
                "class": "form-control"
            }
        )
    )
    last_name = forms.CharField(
        label="Apellido",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Apellido",
                "class": "form-control"
            }
        )
    )
    role = forms.ChoiceField(
        label="Rol",
        choices=User.ROLE_CHOICES,  
        widget=forms.Select(
            attrs={
                "class": "form-control"
            }
        )
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control"
            }
        )
    )
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Contraseña",
                "class": "form-control"
            }
        ))
    password2 = forms.CharField(
        label="Confirmar contraseña",
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

    def clean_CURP(self):
        curp = self.cleaned_data.get("CURP", "").upper()
        curp_regex = r"^[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d$"
        if not re.match(curp_regex, curp):
            raise forms.ValidationError("CURP inválido. Verifica el formato correcto.")
        return curp

    def clean_RFC(self):
        rfc = self.cleaned_data.get("RFC", "").upper()
        rfc_regex = r"^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$"
        if not re.match(rfc_regex, rfc):
            raise forms.ValidationError("RFC inválido. Verifica el formato correcto.")
        return rfc

    
# AsignaturaForm
class AsignaturaForm(forms.ModelForm):
    nombre = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre de la asignatura"}))
    clave = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Clave"}))
    matricula = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Matrícula"}))
    carrera = forms.ModelChoiceField(queryset=Carrera.objects.all(), widget=forms.Select(attrs={"class": "form-control"}))
    periodo = forms.ModelChoiceField(queryset=Periodo.objects.all(), widget=forms.Select(attrs={"class": "form-control"}))

    class Meta:
        model = Asignatura
        fields = ["nombre", "clave", "matricula", "carrera", "periodo"]


# GrupoForm
class GrupoForm(forms.ModelForm):
    nombre = forms.CharField(
        label="Nombre del grupo",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Nombre del grupo"
        })
    )

    class Meta:
        model = Grupo
        fields = ['nombre']



    
class CarreraForm(forms.ModelForm):
    clave = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Código de la carrera", "class": "form-control"}
        )
    )
    nombre = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Nombre de la carrera", "class": "form-control"}
        )
    )
    horas_semanales = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={"placeholder": "Horas Semanales", "class": "form-control", "min": 1}
        ),
        min_value=1,
        error_messages={
            "invalid": "Ingresa solo números.",
            "required": "Este campo es obligatorio.",
            "min_value": "Debe ser al menos 1 hora."
        }
    )
    class Meta:
        model = Carrera
        fields = ["nombre", "clave", "horas_semanales"]

# HorarioForm
class HorarioForm(forms.ModelForm):
    class Meta:
        model = Horario
        fields = ['materia', 'docente', 'dia', 'hora']
        widgets = {
            'materia': forms.Select(attrs={'class': 'form-control'}),
            'docente': forms.Select(attrs={'class': 'form-control'}),
            'dia': forms.Select(attrs={'class': 'form-control'}),
            'hora': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        materia = cleaned_data.get('materia')
        docente = cleaned_data.get('docente')

        if materia and docente:
            horarios_existentes = Horario.objects.filter(materia=materia, docente=docente)

            if self.instance.pk:
                horarios_existentes = horarios_existentes.exclude(pk=self.instance.pk)

            if horarios_existentes.count() >= 3:
                raise forms.ValidationError("Esta materia ya tiene asignados 3 horarios con este docente.")
    
    # DisponibilidadForm
class DisponibilidadForm(forms.ModelForm):
    class Meta:
        model = Disponibilidad
        fields = ['materia', 'dia', 'hora_inicio', 'hora_fin']
        widgets = {
            'materia': forms.Select(attrs={'class': 'form-control'}),
            'dia': forms.Select(attrs={'class': 'form-control'}),
            'hora_inicio': forms.Select(attrs={'class': 'form-control'}),
            'hora_fin': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.docente = kwargs.pop('docente', None)
        super().__init__(*args, **kwargs)

        # Opción: si quieres filtrar por carrera (si la materia tiene relación con carrera)
        if "carrera" in self.data:
            try:
                carrera_id = int(self.data.get("carrera"))
                self.fields["materia"].queryset = Asignatura.objects.filter(carrera_id=carrera_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.materia and self.instance.materia.carrera:
            self.fields["materia"].queryset = Asignatura.objects.filter(carrera=self.instance.materia.carrera)
        else:
            self.fields["materia"].queryset = Asignatura.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')
        dia = cleaned_data.get('dia')

        if not (hora_inicio and hora_fin and self.docente):
            return cleaned_data

        h_ini = int(hora_inicio.split(":")[0])
        h_fin = int(hora_fin.split(":")[0])
        nuevas_horas = h_fin - h_ini

        # Sumar horas ya registradas
        total_horas = 0
        disponibilidades = Disponibilidad.objects.filter(docente=self.docente)
        if self.instance.pk:
            disponibilidades = disponibilidades.exclude(pk=self.instance.pk)

        for d in disponibilidades:
            hi = int(d.hora_inicio.split(":")[0])
            hf = int(d.hora_fin.split(":")[0])
            total_horas += hf - hi

        if total_horas + nuevas_horas > 18:
            raise forms.ValidationError("Excedes el límite de 18 horas por semana.")

        return cleaned_data
class AdministradorForm(forms.ModelForm):
    nombre = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}))
    apellido_paterno = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido paterno'}))
    apellido_materno = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido materno'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}))
    telefono = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}))
    clave = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Clave'}))

    carrera = forms.ModelChoiceField(
        queryset=Carrera.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Administrador
        fields = ["nombre", "apellido_paterno", "apellido_materno", "email", "telefono", "clave", "carrera"]


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

class PeriodoForm(forms.ModelForm):
    nombre = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Nombre del periodo",
                "class": "form-control text-center"
            }
        )
    )

    class Meta:
        model = Periodo
        fields = ["nombre"]