# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path
from .views import login_view, register_view, logout_view, superadmin_dashboard, admin_dashboard, docente_dashboard
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', login_view, name="login"),
    path('register/', register_view, name="register"),
    path("logout/", logout_view, name="logout"),
    path("dashboard/superadmin/", superadmin_dashboard, name="superadmin_dashboard"),
    path("dashboard/admin/", admin_dashboard, name="admin_dashboard"),
    path("dashboard/docente/", docente_dashboard, name="docente_dashboard"),
]
