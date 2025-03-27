from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.home.models import User, Docente, Asignatura, Carrera, Horario, Administrador, Grupo, Periodo, Disponibilidad
from .forms import LoginForm, SignUpForm, DocenteForm, AsignaturaForm, CarreraForm, HorarioForm, AdministradorForm, CambiarContraseñaForm, GrupoForm, PeriodoForm, DisponibilidadForm
from django.http import JsonResponse
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.utils.crypto import get_random_string
import random
import string
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db import models
from django.db.models import Q
from django.urls import reverse

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
    docentes = Docente.objects.all()
    return render(request, 'Docentes/docente_list.html', {'docentes': docentes})

@login_required
def docente_create(request):
    if request.method == "POST":
        form = DocenteForm(request.POST, request.FILES)
        if form.is_valid():
            docente = form.save(commit=False)

            # 🔹 Generar una contraseña aleatoria de 10 caracteres
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

            # 🔹 Verificar si el usuario ya existe
            user, created = User.objects.get_or_create(email=docente.email, defaults={
                'role': 'docente',
                'password': make_password(password),  # Guardar la contraseña cifrada
                'is_active': True
            })

            # 🔹 Asociar el usuario al docente solo si se creó un nuevo usuario
            if created:
                # Asociar el usuario creado al docente
                docente.user = user
                docente.save()

                # 🔹 Enviar email con la contraseña generada
                send_mail(
                    'Acceso al Sistema de Gestión de Horarios',
                    f'Hola {docente.nombre},\n\n'
                    f'Tu cuenta ha sido creada en el sistema de gestión de horarios.\n\n'
                    f'🔹 **Email**: {docente.email}\n'
                    f'🔹 **Contraseña**: {password}\n\n'
                    f'⚠️ Te recomendamos cambiar tu contraseña después de iniciar sesión.\n\n'
                    'Saludos,\nEquipo de Administración',
                    'admin@tusistema.com',
                    [docente.email],
                    fail_silently=False,  # Cambiar a `True` si no quieres que falle la ejecución en caso de error
                )

            messages.success(request, "Docente creado exitosamente.")
            return redirect('docente_list')
    else:
        form = DocenteForm()
    
    return render(request, 'Docentes/docente_form.html', {"form": form})


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
    return render(request, 'Docentes/docente_confirm_delete.html', {'docente': docente})

@login_required
def asignatura_list(request):
    query = request.GET.get("q")
    asignaturas = Asignatura.objects.all()
    if query:
        asignaturas = asignaturas.filter(
            Q(nombre__icontains=query) |
            Q(clave__icontains=query) |
            Q(matricula__icontains=query)
        )
    return render(request, "asignaturas/asignatura_list.html", {"asignaturas": asignaturas, "query": query})

@login_required
def asignatura_create(request):
    if request.method == "POST":
        form = AsignaturaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("asignatura_list")
    else:
        form = AsignaturaForm()
    return render(request, "asignaturas/asignatura_form.html", {"form": form})

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
    horarios = Horario.objects.select_related('materia', 'docente')

    dias_dict = {
        'Lunes': 1,
        'Martes': 2,
        'Miércoles': 3,
        'Jueves': 4,
        'Viernes': 5,
        'Sábado': 6,
    }

    eventos = []
    for h in horarios:
        inicio, fin = h.hora.split(' - ')
        eventos.append({
            'title': f"{h.materia.nombre} - {h.docente.nombre}",
            'startTime': inicio,
            'endTime': fin,
            'daysOfWeek': [dias_dict[h.dia]],
            'url_edit': reverse('horario_update', args=[h.id]),
            'url_delete': reverse('horario_delete', args=[h.id]),
        })

    return render(request, 'horarios/horario_list.html', {'eventos': eventos})


@login_required
def horario_create(request):
    form = HorarioForm(request.POST or None)
    disponibilidades = None

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Horario asignado correctamente.")
            return redirect('horario_list')
    else:
        docente_id = request.GET.get('docente') or form.initial.get("docente") or None
        if docente_id:
            disponibilidades = Disponibilidad.objects.filter(docente_id=docente_id)

    return render(request, 'horarios/horario_form.html', {
        'form': form,
        'disponibilidades': disponibilidades
    })

@login_required
def horario_update(request, pk):
    horario = get_object_or_404(Horario, pk=pk)
    form = HorarioForm(request.POST or None, instance=horario)
    if form.is_valid():
        form.save()
        messages.success(request, "Horario actualizado.")
        return redirect('horario_list')
    return render(request, 'horarios/horario_form.html', {'form': form})

@login_required
def horario_delete(request, pk):
    horario = get_object_or_404(Horario, pk=pk)
    if request.method == 'POST':
        horario.delete()
        messages.success(request, "Horario eliminado.")
        return redirect('horario_list')
    return render(request, 'horarios/horario_confirm_delete.html', {'horario': horario})

        
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

            # Generar contraseña
            password = get_random_string(length=10)
            email = administrador.email

            # Validar que no exista el user
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Ya existe un usuario con ese correo.')
                return render(request, 'Administradores/administrador_form.html', {'form': form, 'accion': 'Crear'})

            # Crear usuario
            user = User.objects.create(
                email=email,
                role='admin',
                password=make_password(password),
                is_active=True
            )

            administrador.user = user
            administrador.save()

            # Guardar email y password en sesión
            request.session['admin_email'] = email
            request.session['admin_password'] = password

            # Enviar correo
            send_mail(
                'Acceso al Sistema de Gestión de Horarios',
                f'Hola {administrador.nombre},\n\nTu cuenta ha sido creada.\nCorreo: {email}\nContraseña: {password}',
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
    email = request.session.pop('admin_email', None)
    password = request.session.pop('admin_password', None)

    if not email or not password:
        messages.warning(request, "No hay información del nuevo administrador.")
        return redirect('administrador_list')

    return render(request, 'Administradores/admin_created_success.html', {
        'email': email,
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
    docente = get_object_or_404(Docente, user=request.user)
    disponibilidades = Disponibilidad.objects.filter(docente=docente)
    materias = Asignatura.objects.all()

    dias_dict = {
        'Domingo': 0,
        'Lunes': 1,
        'Martes': 2,
        'Miércoles': 3,
        'Jueves': 4,
        'Viernes': 5,
        'Sábado': 6,
    }

    eventos = []
    for d in disponibilidades:
        eventos.append({
            "title": d.materia.nombre if d.materia else "Disponible",
            "daysOfWeek": [dias_dict[d.dia]],
            "startTime": d.hora_inicio,
            "endTime": d.hora_fin,
            "url_edit": reverse("disponibilidad_update", args=[d.id]),
            "url_delete": reverse("disponibilidad_delete", args=[d.id]),
        })

    return render(request, 'disponibilidad/disponibilidad_list.html', {
        'disponibilidades': disponibilidades,
        'materias': materias,
        'eventos': eventos,  # <<<< necesario para el calendario
    })

@login_required
def disponibilidad_create(request):
    docente = get_object_or_404(Docente, user=request.user)
    if request.method == 'POST':
        form = DisponibilidadForm(request.POST, docente=docente)
        if form.is_valid():
            disponibilidad = form.save(commit=False)
            disponibilidad.docente = docente
            disponibilidad.save()
            messages.success(request, "Disponibilidad registrada.")
            return redirect('disponibilidad_list')
    else:
        form = DisponibilidadForm(docente=docente)
    
    return render(request, 'disponibilidad/disponibilidad_form.html', {'form': form})


@login_required
def disponibilidad_update(request, pk):
    disponibilidad = get_object_or_404(Disponibilidad, pk=pk)
    if request.method == 'POST':
        form = DisponibilidadForm(request.POST, instance=disponibilidad)
        if form.is_valid():
            form.save()
            messages.success(request, 'Disponibilidad actualizada.')
            return redirect('disponibilidad_list')
    else:
        form = DisponibilidadForm(instance=disponibilidad)
    return render(request, 'disponibilidad/disponibilidad_form.html', {'form': form})

@login_required
def disponibilidad_delete(request, pk):
    disponibilidad = get_object_or_404(Disponibilidad, pk=pk)
    if request.method == 'POST':
        disponibilidad.delete()
        messages.success(request, 'Disponibilidad eliminada.')
        return redirect('disponibilidad_list')
    return render(request, 'disponibilidad/disponibilidad_confirm_delete.html', {'disponibilidad': disponibilidad})


@login_required
def mi_horario_view(request):
    docente = get_object_or_404(Docente, user=request.user)
    horarios = Horario.objects.filter(docente=docente).select_related('materia')

    eventos = []
    dias_dict = {'Lunes': 1, 'Martes': 2, 'Miércoles': 3, 'Jueves': 4, 'Viernes': 5, 'Sábado': 6}
    
    for h in horarios:
        hora_inicio, hora_fin = h.hora.split(" - ")
        eventos.append({
            'title': f'{h.materia.nombre}',
            'daysOfWeek': [dias_dict[h.dia]],
            'startTime': hora_inicio,
            'endTime': hora_fin,
        })

    return render(request, 'Docentes/mi_horario.html', {
        'eventos': eventos,
        'docente': docente,
    })