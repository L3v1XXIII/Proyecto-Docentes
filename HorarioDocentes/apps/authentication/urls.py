# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path
from .views import login_view, register_view, logout_view, superadmin_dashboard, admin_dashboard, docente_dashboard, user_list, user_create, user_delete, user_update, docente_list, docente_create, docente_delete, docente_update
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
]
