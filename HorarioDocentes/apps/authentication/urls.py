# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path
from .views import asignatura_create, asignatura_delete, asignatura_list, asignatura_update, carrera_create, carrera_delete, carrera_list, carrera_update, horario_create, horario_delete, horario_list, horario_update, administrador_create, administrador_delete, administrador_list, administrador_update, grupo_create, grupo_delete, grupo_list, grupo_update, disponibilidad_create, disponibilidad_delete, disponibilidad_list, disponibilidad_update
from .views import login_view, register_view, logout_view, dashboard, superadmin_dashboard, admin_dashboard, docente_dashboard, user_list, user_create, user_delete, user_update, docente_list, docente_create, docente_delete, docente_update, perfil_usuario, cambiar_contraseña, admin_created_success, periodo_create, periodo_delete, periodo_list, periodo_update, mi_horario_view
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', login_view, name="login"),
    path('register/', register_view, name="register"),
    path("logout/", logout_view, name="logout"),
    
    path("dashboard/superadmin/", superadmin_dashboard, name="superadmin_dashboard"),
    path("dashboard/admin/", admin_dashboard, name="admin_dashboard"),
    path("dashboard/docente/", docente_dashboard, name="docente_dashboard"),
    path("dashboard/", dashboard, name="dashboard"),
    
    path("users/", user_list, name="user_list"), 
    path("users/create/", user_create, name="user_create"), 
    path("users/update/<int:pk>/", user_update, name="user_update"), 
    path("users/delete/<int:pk>/", user_delete, name="user_delete"), 
    
    path('docentes/', docente_list, name='docente_list'),
    path('docentes/create/', docente_create, name='docente_create'),
    path('docentes/update/<int:pk>/', docente_update, name='docente_update'),
    path('docentes/delete/<int:pk>/', docente_delete, name='docente_delete'),
    
    path("asignaturas/", asignatura_list, name="asignatura_list"),
    path("asignaturas/create/", asignatura_create, name="asignatura_create"),
    path("asignaturas/<int:pk>/edit/", asignatura_update, name="asignatura_update"),
    path("asignaturas/<int:pk>/delete/", asignatura_delete, name="asignatura_delete"),
    
    path('carreras/', carrera_list, name='carrera_list'),
    path('carreras/create/', carrera_create, name='carrera_create'),
    path('carreras/update/<int:pk>/', carrera_update, name='carrera_update'),
    path('carreras/delete/<int:pk>/', carrera_delete, name='carrera_delete'),
    
    path('horarios/', horario_list, name='horario_list'),
    path('horarios/create/', horario_create, name='horario_create'),
    path('horarios/update/<int:pk>/', horario_update, name='horario_update'),
    path('horarios/delete/<int:pk>/', horario_delete, name='horario_delete'),
    
    path('administradores/', administrador_list, name='administrador_list'),
    path('administradores/create/', administrador_create, name='administrador_create'),
    path('administradores/creado/', admin_created_success, name='admin_created_success'),
    path('administradores/update/<int:pk>/', administrador_update, name='administrador_update'),
    path('administradores/delete/<int:pk>/', administrador_delete, name='administrador_delete'),
    
    path('perfil/', perfil_usuario, name='perfil_usuario'),
    path('perfil/cambiar-contraseña/', cambiar_contraseña, name='cambiar_contraseña'),
    
    path('grupos/', grupo_list, name='grupo_list'),
    path('grupos/create/', grupo_create, name='grupo_create'),
    path('grupos/<int:pk>/edit/', grupo_update, name='grupo_update'),
    path('grupos/<int:pk>/delete/', grupo_delete, name='grupo_delete'),
    
    path('periodo/', periodo_list, name='periodo_list'),
    path('periodo/create/', periodo_create, name='periodo_create'),
    path('periodo/<int:pk>/edit/', periodo_update, name='periodo_update'),
    path('periodo/<int:pk>/delete/', periodo_delete, name='periodo_delete'),
    
    path('disponibilidades/', disponibilidad_list, name='disponibilidad_list'),
    path('disponibilidades/create/', disponibilidad_create, name='disponibilidad_create'),
    path('disponibilidades/<int:pk>/update/', disponibilidad_update, name='disponibilidad_update'),
    path('disponibilidades/<int:pk>/delete/', disponibilidad_delete, name='disponibilidad_delete'),
    
    path('MiHorario/', mi_horario_view, name='mi_horario'),
    

]
