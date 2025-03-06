# -*- encoding: utf-8 -*-

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from apps.home.models import User, Docente
from django.contrib.auth import authenticate


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
        fields = ["nombre", "apellido_paterno", "apellido_materno", "email", "telefono", "area", "matricula", "CURP", "RFC", "comprobante_domicilio", "titulo"]
