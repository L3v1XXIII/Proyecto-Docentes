from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.home.models import User
from .forms import LoginForm, SignUpForm

def login_view(request):
    form = LoginForm(request.POST or None)
    msg = None

    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()  # Obtener el usuario autenticado
            
            print(f"Usuario autenticado: {user}")

            if user is not None:
                login(request, user)
                print(f"Usuario {user.email} autenticado correctamente")
                return redirect_dashboard(user)
            else:
                msg = 'Datos incorrectos'
                print("Autenticación fallida. Credenciales incorrectas.")
        else:
            msg = 'Error en el formulario de login'
            print(f"Errores en el formulario: {form.errors}")

    return render(request, "accounts/login.html", {"form": form, "msg": msg})



def register_view(request):
    form = SignUpForm(request.POST or None)
    msg = None
    success = False
    if request.method == "POST":
        if form.is_valid():
            user = form.save()
            messages.success(request, "Usuario registrado con éxito. Ahora puedes iniciar sesión.")
            return redirect("login")  # Redirigir a la página de login
        else:
            msg = "Hubo un error en el formulario"
    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect("login")


def redirect_dashboard(user):
    if user.role == 'superadmin':
        return redirect('superadmin_dashboard')
    elif user.role == 'admin':
        return redirect('admin_dashboard')
    elif user.role == 'docente':
        return redirect('docente_dashboard')
    return redirect('/')  # En caso de algún error


@login_required
def superadmin_dashboard(request):
    return render(request, 'dashboards/dash_sp.html')


@login_required
def admin_dashboard(request):
    return render(request, 'dashboards/dash_admin.html')


@login_required
def docente_dashboard(request):
    return render(request, 'dashboards/dash_docente.html')
