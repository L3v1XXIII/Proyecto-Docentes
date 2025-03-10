# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path
from .views import login_view, register_view, logout_view, superadmin_dashboard, admin_dashboard, docente_dashboard, user_list, user_create, user_delete, user_update, docente_list, docente_create, docente_delete, docente_update, asignatura_create, asignatura_delete, asignatura_list, asignatura_update, carrera_create, carrera_delete, carrera_list, carrera_update, horario_create, horario_delete, horario_list, horario_update
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', login_view, name="login"),
    path('register/', register_view, name="register"),
    path("logout/", logout_view, name="logout"),
    
    path("dashboard/superadmin/", superadmin_dashboard, name="superadmin_dashboard"),
    path("dashboard/admin/", admin_dashboard, name="admin_dashboard"),
    path("dashboard/docente/", docente_dashboard, name="docente_dashboard"),
    
    path("users/", user_list, name="user_list"), 
    path("users/create/", user_create, name="user_create"), 
    path("users/update/<int:pk>/", user_update, name="user_update"), 
    path("users/delete/<int:pk>/", user_delete, name="user_delete"), 
    
    path('docentes/', docente_list, name='docente_list'),
    path('docentes/create/', docente_create, name='docente_create'),
    path('docentes/update/<int:pk>/', docente_update, name='docente_update'),
    path('docentes/delete/<int:pk>/', docente_delete, name='docente_delete'),
    
    path('asignaturas/', asignatura_list, name='asignatura_list'),
    path('asignaturas/create/', asignatura_create, name='asignatura_create'),
    path('asignaturas/update/<int:pk>/', asignatura_update, name='asignatura_update'),
    path('asignaturas/delete/<int:pk>/', asignatura_delete, name='asignatura_delete'),
    
    path('carreras/', carrera_list, name='carrera_list'),
    path('carreras/create/', carrera_create, name='carrera_create'),
    path('carreras/update/<int:pk>/', carrera_update, name='carrera_update'),
    path('carreras/delete/<int:pk>/', carrera_delete, name='carrera_delete'),
    
    path('horarios/', horario_list, name='horario_list'),
    path('horarios/create/', horario_create, name='horario_create'),
    path('horarios/update/<int:pk>/', horario_update, name='horario_update'),
    path('horarios/delete/<int:pk>/', horario_delete, name='horario_delete'),
]
