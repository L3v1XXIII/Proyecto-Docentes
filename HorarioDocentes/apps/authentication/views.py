# -*- encoding: utf-8 -*-

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from apps.home.models import Docente
from .forms import LoginForm, SignUpForm, DocenteForm 


def login_view(request):
    form = LoginForm(request.POST or None)
    msg = None
    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            print("Username:", username)
            print("Password:", password)
            user = authenticate(username=username, password=password)
            print("User:", user)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'
    return render(request, "accounts/login.html", {"form": form, "msg": msg})

def register_user(request):
    msg = None
    success = False
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            msg = 'User created - please <a href="/login">login</a>.'
            success = True
        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()
    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})
 

def docente_list(request):
    docentes = Docente.objects.all()
    return render(request, 'Docentes/docente_list.html', {'docentes': docentes})

def docente_create(request):
    if request.method == 'POST':
        form = DocenteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('docente_list')
    else:
        form = DocenteForm()
    return render(request, 'Docentes/docente_form.html', {'form': form})

def docente_update(request, pk):
    docente = get_object_or_404(Docente, pk=pk)
    if request.method == 'POST':
        form = DocenteForm(request.POST, instance=docente)
        if form.is_valid():
            form.save()
            return redirect('Docente_list')
    else:
        form = DocenteForm(instance=docente)
    return render(request, 'Docentes/docente_form.html', {'form': form})

def docente_delete(request, pk):
    docente = get_object_or_404(Docente, pk=pk)
    if request.method == 'POST':
        docente.delete()
        return redirect('docente_list')
    return render(request, 'Docentes/docente_confirm_delete.html', {'docente': docente})