from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.home.models import User, Docente, Asignatura, Carrera
from .forms import LoginForm, SignUpForm, DocenteForm, AsignaturaForm, CarreraForm

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

@login_required
def user_list(request):
    users = User.objects.all()
    return render(request, 'users/user_list.html', {'users': users})

@login_required
def user_create(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario creado exitosamente.")
            return redirect('user_list')
    else:
        form = SignUpForm()
    return render(request, 'users/user_form.html', {'form': form})

@login_required
def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = SignUpForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario actualizado exitosamente.")
            return redirect('user_list')
    else:
        form = SignUpForm(instance=user)
    return render(request, 'users/user_form.html', {'form': form})

@login_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, "Usuario eliminado exitosamente.")
        return redirect('user_list')
    return render(request, 'users/user_confirm_delete.html', {'user': user})

@login_required
def docente_list(request):
    docentes = Docente.objects.all()
    return render(request, 'Docentes/docente_list.html', {'docentes': docentes})

@login_required
def docente_create(request):
    if request.method == 'POST':
        form = DocenteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Docente creado exitosamente.")
            return redirect('docente_list')
    else:
        form = DocenteForm()
    return render(request, 'Docentes/docente_form.html', {'form': form})

@login_required
def docente_update(request, pk):
    docente = get_object_or_404(Docente, pk=pk)
    if request.method == 'POST':
        form = DocenteForm(request.POST, instance=docente)
        if form.is_valid():
            form.save()
            messages.success(request, "Docente actualizado exitosamente.")
            return redirect('docente_list')
    else:
        form = DocenteForm(instance=docente)
    return render(request, 'Docentes/docente_form.html', {'form': form})

@login_required
def docente_delete(request, pk):
    docente = get_object_or_404(Docente, pk=pk)
    if request.method == 'POST':
        docente.delete()
        messages.success(request, "Docente eliminado exitosamente.")
        return redirect('docente_list')
    return render(request, 'docentes/docente_confirm_delete.html', {'docente': docente})

@login_required
def asignatura_list(request):
    asignaturas = Asignatura.objects.all()
    return render(request, 'asignaturas/asignatura_list.html', {'asignaturas': asignaturas})

@login_required
def asignatura_create(request):
    if request.method == 'POST':
        form = AsignaturaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Asignatura creada exitosamente.")
            return redirect('asignatura_list')
    else:
        form = AsignaturaForm()
    return render(request, 'asignaturas/asignatura_form.html', {'form': form})

@login_required
def asignatura_update(request, pk):
    asignatura = get_object_or_404(Asignatura, pk=pk)
    if request.method == 'POST':
        form = AsignaturaForm(request.POST, instance=asignatura)
        if form.is_valid():
            form.save()
            messages.success(request, "Asignatura actualizada exitosamente.")
            return redirect('asignatura_list')
    else:
        form = AsignaturaForm(instance=asignatura)
    return render(request, 'asignaturas/asignatura_form.html', {'form': form})

@login_required
def asignatura_delete(request, pk):
    asignatura = get_object_or_404(Asignatura, pk=pk)
    if request.method == 'POST':
        asignatura.delete()
        messages.success(request, "Asignatura eliminada exitosamente.")
        return redirect('asignatura_list')
    return render(request, 'asignaturas/asignatura_confirm_delete.html', {'asignatura': asignatura})

@login_required
def carrera_list(request):
    carreras = Carrera.objects.all()
    return render(request, 'carreras/carrera_list.html', {'carreras': carreras})

@login_required
def carrera_create(request):
    if request.method == 'POST':
        form = CarreraForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Carrera creada exitosamente.")
            return redirect('carrera_list')
    else:
        form = CarreraForm()
    return render(request, 'carreras/carrera_form.html', {'form': form})

@login_required
def carrera_update(request, pk):
    carrera = get_object_or_404(Carrera, pk=pk)
    if request.method == 'POST':
        form = CarreraForm(request.POST, instance=carrera)
        if form.is_valid():
            form.save()
            messages.success(request, "Carrera actualizada exitosamente.")
            return redirect('carrera_list')
    else:
        form = CarreraForm(instance=carrera)
    return render(request, 'carreras/carrera_form.html', {'form': form})

@login_required
def carrera_delete(request, pk):
    carrera = get_object_or_404(Carrera, pk=pk)
    if request.method == 'POST':
        carrera.delete()
        messages.success(request, "Carrera eliminada exitosamente.")
        return redirect('carrera_list')
    return render(request, 'carreras/carrera_confirm_delete.html', {'carrera': carrera})