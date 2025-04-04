from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.home.models import User, Docente, Asignatura, Carrera, Horario, Administrador, Grupo, Periodo, HorarioAsignatura, DisponibilidadDocente, HorarioDocente
from .forms import LoginForm, SignUpForm, DocenteForm, AsignaturaForm, CarreraForm, AdministradorForm, CambiarContraseñaForm, GrupoForm, PeriodoForm, DisponibilidadDocenteForm, HorarioAsignaturaForm
from django.http import JsonResponse
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.utils.crypto import get_random_string
from datetime import datetime
import random
import string
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.template.loader import get_template
from django.forms import modelformset_factory

def login_view(request):
    form = LoginForm(request.POST or None)
    msg = None

    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Bienvenido, {user.username}")
            return redirect_dashboard(user)
        else:
            msg = "Usuario o contraseña incorrectos."

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
def dashboard(request):
    return render(request, 'dashboards/dash_central.html')

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
    query = request.GET.get('q', '')
    users = User.objects.filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(email__icontains=query) |
        Q(role__icontains=query)
    ) if query else User.objects.all()

    return render(request, 'users/user_list.html', {'users': users, 'query': query})

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
    user = request.user

    if user.role == 'admin':
        administrador = Administrador.objects.filter(user=user).first()
        if administrador and administrador.carreras.exists():
            docentes = Docente.objects.filter(carrera__in=administrador.carreras.all())
        else:
            docentes = Docente.objects.none()
    else:
        docentes = Docente.objects.all()  # Superadmin u otros roles

    return render(request, 'Docentes/docente_list.html', {"docentes": docentes})


@login_required
def docente_create(request):
    if request.method == "POST":
        form = DocenteForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            docente = form.save(commit=False)

            password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            username = docente.matricula
            email = docente.email

            if User.objects.filter(username=username).exists():
                messages.error(request, 'Ya existe un usuario con esa matrícula.')
                return render(request, 'Docentes/docente_form.html', {"form": form})

            if User.objects.filter(email=email).exists():
                messages.error(request, 'Ya existe un usuario con ese correo.')
                return render(request, 'Docentes/docente_form.html', {"form": form})

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role='docente',
                is_active=True
            )

            docente.user = user
            docente.save()

            request.session['docente_username'] = username
            request.session['docente_password'] = password

            send_mail(
                'Acceso al Sistema de Gestión de Horarios',
                f'Hola {docente.nombre},\n\n'
                f'Tu cuenta ha sido creada.\nUsuario: {username}\nContraseña: {password}',
                'admin@tusistema.com',
                [email],
                fail_silently=False,
            )

            return redirect('docente_created_success')
    else:
        form = DocenteForm(user=request.user)  # Pasamos el usuario en el formulario

    return render(request, 'Docentes/docente_form.html', {"form": form})




@login_required
def docente_update(request, pk):
    docente = get_object_or_404(Docente, pk=pk)
    if request.method == 'POST':
        form = DocenteForm(request.POST, instance=docente, user=request.user)  # Pasamos el usuario
        if form.is_valid():
            form.save()
            messages.success(request, "Docente actualizado exitosamente.")
            return redirect('docente_list')
    else:
        form = DocenteForm(instance=docente, user=request.user)  # Aseguramos de pasar el usuario en el GET

    return render(request, 'Docentes/docente_form.html', {'form': form})


@login_required
def docente_delete(request, pk):
    docente = get_object_or_404(Docente, pk=pk)
    if request.method == 'POST':
        docente.delete()
        messages.success(request, "Docente eliminado exitosamente.")
        return redirect('docente_list')
    return render(request, 'Docentes/docente_confirm_delete.html', {'docente': docente})

@login_required
def asignatura_list(request):
    user = request.user

    if user.role == 'admin':
        administrador = Administrador.objects.filter(user=user).first()
        if administrador and administrador.carreras.exists():
            asignaturas = Asignatura.objects.filter(
                models.Q(carrera__in=administrador.carreras.all()) | models.Q(visible_para_todos=True)
            )
        else:
            asignaturas = Asignatura.objects.filter(visible_para_todos=True)
    else:
        asignaturas = Asignatura.objects.all()

    return render(request, 'Asignaturas/asignatura_list.html', {'asignaturas': asignaturas})




@login_required
def asignatura_create(request):
    form = AsignaturaForm(request.POST or None, user=request.user)

    if request.method == "POST":
        if form.is_valid():
            asignatura = form.save(commit=False)
            asignatura.save()
            messages.success(request, "Asignatura creada correctamente.")
            return redirect("asignatura_list")
        else:
            messages.error(request, "Corrige los errores del formulario.")

    return render(request, "Asignaturas/asignatura_form.html", {"form": form})

@login_required
def asignatura_update(request, pk):
    asignatura = get_object_or_404(Asignatura, pk=pk)
    if request.method == "POST":
        form = AsignaturaForm(request.POST, instance=asignatura)
        if form.is_valid():
            form.save()
            return redirect("asignatura_list")
    else:
        form = AsignaturaForm(instance=asignatura)
    return render(request, "asignaturas/asignatura_form.html", {"form": form})

@login_required
def asignatura_delete(request, pk):
    asignatura = get_object_or_404(Asignatura, pk=pk)
    if request.method == "POST":
        asignatura.delete()
        return redirect("asignatura_list")
    return render(request, "asignaturas/asignatura_confirm_delete.html", {"asignatura": asignatura})


@login_required
def carrera_list(request):
    query = request.GET.get('q', '')
    carreras = Carrera.objects.filter(
        Q(nombre__icontains=query) |
        Q(clave__icontains=query)
    ) if query else Carrera.objects.all()

    return render(request, 'carreras/carrera_list.html', {
        'carreras': carreras,
        'query': query
    })

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

@login_required
def horario_list(request):
    horarios = HorarioAsignatura.objects.all()
    return render(request, 'horarios/horario_list.html', {'horarios': horarios})

# Vista para crear o editar un horario
@login_required
def horario_create(request):
    user = request.user
    error_message = None
    overlap_message = None  # Nuevo mensaje para el solapamiento

    # Verificar el rol del usuario (si es administrador)
    if user.role == 'admin':
        administrador = Administrador.objects.filter(user=user).first()
        if administrador and administrador.carreras.exists():
            asignaturas = Asignatura.objects.filter(
                models.Q(carrera__in=administrador.carreras.all()) | models.Q(visible_para_todos=True)
            )
        else:
            asignaturas = Asignatura.objects.filter(visible_para_todos=True)
    else:
        asignaturas = Asignatura.objects.all()

    # Obtener el formulario
    form = HorarioAsignaturaForm(request.POST or None)
    
    if request.method == "POST":
        if form.is_valid():
            horario = form.save(commit=False)
            asignatura = horario.asignatura

            # Verificar si la suma total de horas excede 3 horas
            total_duracion = sum(
                (h.hora_fin.hour - h.hora_inicio.hour) * 60 + (h.hora_fin.minute - h.hora_inicio.minute)
                for h in HorarioAsignatura.objects.filter(asignatura=asignatura)
            ) + (horario.hora_fin.hour - horario.hora_inicio.hour) * 60 + (horario.hora_fin.minute - horario.hora_inicio.minute)

            # Si excede 3 horas, mostrar un mensaje de advertencia
            if total_duracion > 180:
                error_message = "La asignatura excede el límite de 3 horas semanales."

            # Verificar si hay solapamientos de horarios
            overlapping_hours = HorarioAsignatura.objects.filter(
                asignatura=asignatura,
                dia=horario.dia,
                hora_inicio__lt=horario.hora_fin,
                hora_fin__gt=horario.hora_inicio
            ).exclude(pk=horario.pk)  # Excluir el horario actual de la comprobación de solapamiento

            if overlapping_hours.exists():
                overlap_message = "Este horario se solapa con otro horario de la asignatura."

            if not error_message and not overlap_message:
                # Guardar el horario si no hay error ni solapamiento
                horario.save()
                return redirect("horario_list")

    return render(request, "horarios/horario_form.html", {
        'form': form,
        'asignaturas': asignaturas,
        'error_message': error_message,  # Pasar el mensaje de error si excede el límite de horas
        'overlap_message': overlap_message,  # Pasar el mensaje de solapamiento si existe
    })




# Vista para actualizar un horario
@login_required
def horario_update(request, pk):
    horario = get_object_or_404(HorarioAsignatura, pk=pk)
    form = HorarioAsignaturaForm(request.POST or None, instance=horario)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Horario actualizado con éxito.")
            return redirect("horario_list")
        else:
            messages.error(request, "Error al actualizar el horario.")

    return render(request, "horarios/horario_form.html", {"form": form})

# Vista para eliminar un horario
@login_required
def horario_delete(request, pk):
    horario = get_object_or_404(HorarioAsignatura, pk=pk)

    if request.method == "POST":
        horario.delete()
        messages.success(request, "Horario eliminado con éxito.")
        return redirect("horario_list")

    return render(request, "horarios/horario_confirm_delete.html", {"horario": horario})
        
# Listar Administradores
@login_required
def administrador_list(request):
    query = request.GET.get('q')  # 👈 Obtener el término de búsqueda
    administradores = Administrador.objects.all()

    if query:
        administradores = administradores.filter(
            Q(nombre__icontains=query) |
            Q(apellido_paterno__icontains=query) |
            Q(apellido_materno__icontains=query) |
            Q(email__icontains=query)
        )

    return render(request, 'Administradores/administrador_list.html', {
        'administradores': administradores,
        'query': query,
    })
# Crear Administrador
@login_required
def administrador_create(request):
    if request.method == 'POST':
        form = AdministradorForm(request.POST)
        if form.is_valid():
            administrador = form.save(commit=False)
            password = get_random_string(length=10)
            email = administrador.email
            clave = administrador.clave  # usamos la clave como username

            # Validar que no exista el usuario por username o email
            if User.objects.filter(username=clave).exists():
                messages.error(request, 'Ya existe un usuario con esa clave.')
                return render(request, 'Administradores/administrador_form.html', {'form': form, 'accion': 'Crear'})

            if User.objects.filter(email=email).exists():
                messages.error(request, 'Ya existe un usuario con ese correo.')
                return render(request, 'Administradores/administrador_form.html', {'form': form, 'accion': 'Crear'})

            # Crear usuario
            user = User.objects.create(
                username=clave,
                email=email,
                role='admin',
                password=make_password(password),
                is_active=True
            )

            administrador.user = user
            administrador.save()

            # Guardar datos en sesión por si quieres mostrarlos en otra vista
            request.session['admin_email'] = email
            request.session['admin_password'] = password
            request.session['admin_username'] = clave

            send_mail(
                'Acceso al Sistema de Gestión de Horarios',
                f'Hola {administrador.nombre},\n\n'
                f'Tu cuenta ha sido creada.\n\n'
                f'🔹 Usuario: {clave}\n'
                f'🔹 Contraseña: {password}\n\n'
                f'⚠️ Te recomendamos cambiar tu contraseña después de iniciar sesión.',
                'admin@tusistema.com',
                [email],
                fail_silently=False,
            )

            return redirect('admin_created_success')
        else:
            messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = AdministradorForm()

    return render(request, 'Administradores/administrador_form.html', {'form': form, 'accion': 'Crear'})

@login_required
def admin_created_success(request):
    username = request.session.pop('admin_username', None)
    password = request.session.pop('admin_password', None)

    if not username or not password:
        messages.warning(request, "No hay información del nuevo administrador.")
        return redirect('administrador_list')

    return render(request, 'Administradores/admin_created_success.html', {
        'username': username,
        'password': password
    })

# Editar Administrador
@login_required
def administrador_update(request, pk):
    administrador = get_object_or_404(Administrador, pk=pk)
    if request.method == "POST":
        form = AdministradorForm(request.POST, instance=administrador)
        if form.is_valid():
            form.save()
            return redirect('administrador_list')
    else:
        form = AdministradorForm(instance=administrador)
    return render(request, 'Administradores/administrador_form.html', {'form': form})

# Eliminar Administrador
@login_required
def administrador_delete(request, pk):
    administrador = get_object_or_404(Administrador, pk=pk)
    if request.method == "POST":
        administrador.delete()
        return redirect('administrador_list')
    return render(request, 'Administradores/administrador_confirm_delete.html', {'administrador': administrador})

@login_required
def perfil_usuario(request):
    return render(request, 'perfil/perfil_usuario.html', {'user': request.user})

@login_required
def cambiar_contraseña(request):
    if request.method == 'POST':
        form = CambiarContraseñaForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Mantiene la sesión después del cambio de contraseña
            messages.success(request, "Contraseña actualizada correctamente.")
            return redirect('perfil_usuario')
        else:
            messages.error(request, "Por favor, corrige los errores.")
    else:
        form = CambiarContraseñaForm(user=request.user)

    return render(request, 'perfil/cambiar_contraseña.html', {'form': form})

@login_required
def grupo_list(request):
    query = request.GET.get('q', '')
    grupos = Grupo.objects.filter(nombre__icontains=query) if query else Grupo.objects.all()
    return render(request, 'grupos/grupo_list.html', {'grupos': grupos, 'query': query})

@login_required
def grupo_create(request):
    if request.method == 'POST':
        form = GrupoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Grupo creado correctamente.')
            return redirect('grupo_list')
    else:
        form = GrupoForm()
    return render(request, 'grupos/grupo_form.html', {'form': form, 'accion': 'Crear'})

@login_required
def grupo_update(request, pk):
    grupo = get_object_or_404(Grupo, pk=pk)
    if request.method == 'POST':
        form = GrupoForm(request.POST, instance=grupo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Grupo actualizado correctamente.')
            return redirect('grupo_list')
    else:
        form = GrupoForm(instance=grupo)
    return render(request, 'grupos/grupo_form.html', {'form': form, 'accion': 'Editar'})

@login_required
def grupo_delete(request, pk):
    grupo = get_object_or_404(Grupo, pk=pk)
    if request.method == 'POST':
        grupo.delete()
        messages.success(request, 'Grupo eliminado correctamente.')
        return redirect('grupo_list')
    return render(request, 'grupos/grupo_confirm_delete.html', {'grupo': grupo})

@login_required
def periodo_list(request):
    query = request.GET.get("q")
    if query:
        periodos = Periodo.objects.filter(nombre__icontains=query)
    else:
        periodos = Periodo.objects.all()
    return render(request, 'periodos/periodo_list.html', {'periodos': periodos, 'query': query})

@login_required
def periodo_create(request):
    if request.method == 'POST':
        form = PeriodoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Periodo creado exitosamente.')
            return redirect('periodo_list')
    else:
        form = PeriodoForm()
    return render(request, 'periodos/periodo_form.html', {'form': form})

@login_required
def periodo_update(request, pk):
    periodo = get_object_or_404(Periodo, pk=pk)
    if request.method == 'POST':
        form = PeriodoForm(request.POST, instance=periodo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Periodo actualizado exitosamente.')
            return redirect('periodo_list')
    else:
        form = PeriodoForm(instance=periodo)
    return render(request, 'periodos/periodo_form.html', {'form': form})

@login_required
def periodo_delete(request, pk):
    periodo = get_object_or_404(Periodo, pk=pk)
    if request.method == 'POST':
        periodo.delete()
        messages.success(request, 'Periodo eliminado exitosamente.')
        return redirect('periodo_list')
    return render(request, 'periodos/periodo_confirm_delete.html', {'periodo': periodo})

@login_required
def disponibilidad_list(request):
    query = request.GET.get("q")
    if query:
        disponibilidades = DisponibilidadDocente.objects.filter(
            docente__nombre__icontains=query
        )
    else:
        disponibilidades = DisponibilidadDocente.objects.all()

    return render(request, 'disponibilidad/disponibilidad_list.html', {
        'disponibilidades': disponibilidades,
        'query': query
    })

@login_required
def disponibilidad_create(request):
    docente = request.user.docente
    asignaturas = Asignatura.objects.filter(carrera=docente.carrera)

    if request.method == 'POST':
        form = DisponibilidadDocenteForm(request.POST)
        
        if form.is_valid():  # Verifica si el formulario es válido
            disponibilidad = form.save(commit=False)
            disponibilidad.docente = docente  # Asociamos el docente con la disponibilidad
            
            # Asociamos las asignaturas seleccionadas con la disponibilidad
            selected_asignaturas_ids = request.POST.getlist('asignaturas')  # Obtener las asignaturas seleccionadas
            
            # Agregar las asignaturas seleccionadas a la disponibilidad
            for asignatura_id in selected_asignaturas_ids:
                asignatura = Asignatura.objects.get(id=asignatura_id)
                disponibilidad.asignaturas.add(asignatura)

            # Agregar los horarios asociados con esas asignaturas
            for asignatura_id in selected_asignaturas_ids:
                asignatura = Asignatura.objects.get(id=asignatura_id)
                for horario in asignatura.horarios.all():
                    disponibilidad.horarios.add(horario)

            disponibilidad.save()  # Guardamos la disponibilidad sin calcular las horas

            messages.success(request, "Disponibilidad registrada exitosamente.")
            return redirect('disponibilidad_list')
        else:
            messages.error(request, "Por favor, corrige los errores del formulario.")
    else:
        form = DisponibilidadDocenteForm()

    return render(request, 'disponibilidad/disponibilidad_form.html', {'form': form, 'asignaturas': asignaturas})


@login_required
def disponibilidad_update(request, pk):
    disponibilidad = get_object_or_404(DisponibilidadDocente, pk=pk)
    if request.method == 'POST':
        form = DisponibilidadDocenteForm(request.POST, instance=disponibilidad, user=request.user)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Disponibilidad actualizada exitosamente.")
                return redirect('disponibilidad_list')  # Redirect to the list of disponibilidades
            except ValueError as e:
                # If the total hours exceed the limit, display an error message
                messages.error(request, str(e))
    else:
        form = DisponibilidadDocenteForm(instance=disponibilidad, user=request.user)

    return render(request, 'disponibilidad/disponibilidad_form.html', {'form': form})

@login_required
def disponibilidad_delete(request, pk):
    disponibilidad = get_object_or_404(DisponibilidadDocente, pk=pk)
    if request.method == 'POST':
        disponibilidad.delete()
        messages.success(request, 'Disponibilidad eliminada exitosamente.')
        return redirect('disponibilidad_list')
    return render(request, 'disponibilidad/disponibilidad_confirm_delete.html', {'disponibilidad': disponibilidad})



    horario_dict = {}
    for h in horarios:
        clave = f"{h.dia}-{h.hora.strftime('%H:%M')}"
        horario_dict[clave] = h

    return render(request, 'Docentes/mi_horario.html', {
        'dias': dias,
        'horas': horas,
        'horario_dict': horario_dict,
    })
    
@login_required
def docente_created_success(request):
    username = request.session.pop('docente_username', None)
    password = request.session.pop('docente_password', None)

    if not username or not password:
        messages.warning(request, "No hay información del nuevo docente.")
        return redirect('docente_list')

    return render(request, 'Docentes/docente_created_success.html', {
        'username': username,
        'password': password
    })
@login_required
def carrera_list2(request):
    user = request.user
    if user.role == 'admin':
        administrador = Administrador.objects.filter(user=user).first()
        if administrador:
            carreras = administrador.carreras.all()
            return render(request, 'Horarios/carrera_list.html', {'carreras': carreras})
    return redirect('home')

@login_required
def asignatura_list2(request, carrera_id):
    carrera = get_object_or_404(Carrera, pk=carrera_id)
    asignaturas = Asignatura.objects.filter(carrera=carrera)
    return render(request, 'Horarios/asignatura_list.html', {'asignaturas': asignaturas, 'carrera': carrera})

@login_required
def docente_list2(request, asignatura_id):
    asignatura = get_object_or_404(Asignatura, pk=asignatura_id)
    docentes = Docente.objects.filter(carrera=asignatura.carrera)
    
    if request.method == 'POST':
        # Obtener el ID del docente seleccionado (ahora seleccionamos un solo docente)
        docente_id = request.POST.get('docente')
        
        if docente_id:
            docente = Docente.objects.get(id=docente_id)
            
            # Crear un nuevo HorarioDocente con el docente y la asignatura
            horario_docente = HorarioDocente(
                docente=docente,
                asignatura=asignatura
            )
            # Guardamos primero el objeto HorarioDocente para obtener un 'id'
            horario_docente.save()
            
            # Ahora podemos asociar los horarios de la asignatura al docente
            for horario in asignatura.horarios.all():
                horario_docente.horarios.add(horario)
            
            # Guardamos nuevamente el objeto después de agregar los horarios
            horario_docente.save()
            
            messages.success(request, 'Asignación de horarios realizada exitosamente.')
            return redirect('docente_list', asignatura_id=asignatura.id)

    return render(request, 'Horarios/docente_list.html', {'docentes': docentes, 'asignatura': asignatura})


# Vista en views.py
def mi_horario_view(request):
    # Obtención de horas y días
    horas = ['08:00', '09:00', '10:00']  # Ejemplo
    dias = ['Lunes', 'Martes', 'Miércoles']  # Ejemplo

    horario_dict = {}
    # Aquí llenamos el diccionario con las asignaciones
    # Ejemplo:
    for dia in dias:
        for hora in horas:
            clave = f'{dia}-{hora}'
            # Suponiendo que 'materia' y 'docente' son objetos
            horario_dict[clave] = {
                'materia': 'Matemáticas',  # Solo el nombre de la materia
                'docente': 'Juan Pérez'  # Solo el nombre del docente
            }

    # Pasar el diccionario a la plantilla
    return render(request, 'Docentes/mi_horario.html', {
        'horario_dict': horario_dict,
        'horas': horas,
        'dias': dias
    })


@login_required
def asignar_docente_a_asignatura(request, asignatura_id):
    asignatura = get_object_or_404(Asignatura, pk=asignatura_id)
    docentes = Docente.objects.filter(carrera=asignatura.carrera)

    if request.method == 'POST':
        docente_id = request.POST.get('docente')  # Seleccionamos un solo docente
        selected_horarios = request.POST.getlist('horarios')  # Lista de horarios seleccionados
        
        docente = get_object_or_404(Docente, id=docente_id)
        
        # Crear un objeto HorarioDocente
        horario_docente = HorarioDocente(docente=docente, asignatura=asignatura)
        horario_docente.save()  # Guardamos el objeto para obtener un 'id' valido
        
        # Asociar los horarios seleccionados a este docente
        for horario_id in selected_horarios:
            horario = HorarioAsignatura.objects.get(id=horario_id)
            horario_docente.horarios.add(horario)
        
        # Guardamos los cambios
        horario_docente.save()
        
        messages.success(request, 'Asignación realizada con éxito.')
        return redirect('ver_horario_docente', docente_id=docente.id)  # Redirigimos al detalle de los horarios

    return render(request, 'Horarios/asignar_docente.html', {'docentes': docentes, 'asignatura': asignatura})

def ver_horario_docente(request, docente_id):
    docente = get_object_or_404(Docente, id=docente_id)
    horario_docentes = HorarioDocente.objects.filter(docente=docente)

    return render(request, 'Horarios/ver_horario_docente.html', {'docente': docente, 'horario_docentes': horario_docentes})