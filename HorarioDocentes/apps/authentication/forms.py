# -*- encoding: utf-8 -*-

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from apps.home.models import User, Docente, Asignatura, Carrera, Horario, Administrador, Periodo, Grupo, DisponibilidadDocente, HorarioAsignatura, HorarioDocente
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
import re
import string
from django.db import models 
from datetime import datetime, date
from django.forms import inlineformset_factory, modelformset_factory

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "placeholder": "Usuario",
            "class": "form-control",
            "name": "username"
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "placeholder": "Contraseña",
            "class": "form-control",
            "name": "password"
        })
    )

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("Usuario o contraseña incorrectos.")
            self.user = user
        return self.cleaned_data

    def get_user(self):
        return getattr(self, 'user', None)


class SignUpForm(UserCreationForm):
    username = forms.CharField(
        label="Nombre de usuario",
        widget=forms.TextInput(
            attrs={"placeholder": "Nombre de usuario", "class": "form-control"}
        )
    )
    first_name = forms.CharField(
        label="Nombre",
        widget=forms.TextInput(attrs={"placeholder": "Nombre", "class": "form-control"})
    )
    last_name = forms.CharField(
        label="Apellido",
        widget=forms.TextInput(attrs={"placeholder": "Apellido", "class": "form-control"})
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "Email", "class": "form-control"})
    )
    role = forms.ChoiceField(
        label="Rol",
        choices=User.ROLE_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"})
    )
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"placeholder": "Contraseña", "class": "form-control"})
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={"placeholder": "Confirmar Contraseña", "class": "form-control"})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'role', 'password1', 'password2')


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
    carrera = forms.ModelChoiceField(
        queryset=Carrera.objects.none(),
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False
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
            "area", "matricula", "CURP", "RFC", "comprobante_domicilio", "titulo",
            "carrera"
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

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Verificar si el usuario es un administrador
        if user and user.role == 'admin':
            admin = Administrador.objects.filter(user=user).first()
            if admin:
                self.fields['carrera'].queryset = admin.carreras.all()

    
# AsignaturaForm
class AsignaturaForm(forms.ModelForm):
    nombre = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre de la asignatura"})
    )
    clave = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Clave"})
    )
    matricula = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Matrícula"})
    )
    carrera = forms.ModelChoiceField(
        queryset=Carrera.objects.none(),  # Se configurará dinámicamente en __init__
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False,
        label="Carrera"
    )
    periodo = forms.ModelChoiceField(
        queryset=Periodo.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Periodo"
    )
    Grupo = forms.ModelChoiceField(
        label="Cuatrimestre",
        queryset=Grupo.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"})
    )
    visible_para_todos = forms.BooleanField(
        required=False,
        label="Visible para todos los administradores"
    )

    class Meta:
        model = Asignatura
        fields = ["nombre", "clave", "matricula", "carrera", "periodo", "Grupo", "visible_para_todos"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user and user.role == 'admin':
            admin = Administrador.objects.filter(user=user).first()

            if admin and admin.carreras.exists():
                qs = admin.carreras.all()
                self.fields['carrera'].queryset = qs
                self.fields['carrera'].empty_label = "Selecciona una carrera"
            else:
                self.fields['carrera'].queryset = Carrera.objects.all()
                self.fields['carrera'].empty_label = "Selecciona una carrera"

        else:
            self.fields['carrera'].queryset = Carrera.objects.all()


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
    

    
class AdministradorForm(forms.ModelForm):
    nombre = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}))
    apellido_paterno = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido paterno'}))
    apellido_materno = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido materno'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}))
    telefono = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}))
    clave = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Clave'}))

    carreras = forms.ModelMultipleChoiceField(
        queryset=Carrera.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label="Carreras"
    )

    class Meta:
        model = Administrador
        fields = ["nombre", "apellido_paterno", "apellido_materno", "email", "telefono", "clave", "carreras"]


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
    
class HorarioAsignaturaForm(forms.ModelForm):
    class Meta:
        model = HorarioAsignatura
        fields = ['asignatura', 'dia', 'hora_inicio', 'hora_fin']

HorarioAsignaturaFormSet = modelformset_factory(
    HorarioAsignatura,
    form=HorarioAsignaturaForm,
    extra=0  # Cambia este valor según tus necesidades
)
HorarioFormSet = modelformset_factory(
    HorarioAsignatura,
    fields=['dia', 'hora_inicio', 'hora_fin'],
    extra=1,
    can_delete=True
)

class DisponibilidadDocenteForm(forms.ModelForm):
    asignaturas = forms.ModelMultipleChoiceField(
        queryset=Asignatura.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = DisponibilidadDocente
        fields = ['asignaturas', 'horarios']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Solo asignaturas de la carrera del docente
        if user and user.role == 'docente':
            docente = user.docente
            self.fields['asignaturas'].queryset = Asignatura.objects.filter(carrera=docente.carrera)
            # Asociar los horarios automáticamente con las asignaturas
            for asignatura in self.fields['asignaturas'].queryset:
                self.fields['horarios'].queryset |= asignatura.horarios.all()

class HorarioDocenteForm(forms.ModelForm):
    class Meta:
        model = HorarioDocente
        fields = ['docente', 'asignatura', 'horarios']

    docentes = forms.ModelMultipleChoiceField(
        queryset=Docente.objects.none(),
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and user.role == 'admin':
            # Solo docentes de la carrera seleccionada
            carrera = user.admin.carreras.first()  # Obtener la carrera del admin
            self.fields['docentes'].queryset = Docente.objects.filter(carrera=carrera)
