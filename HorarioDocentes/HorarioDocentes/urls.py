from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect  # 👈 Importa redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('login', permanent=False)),  # 👈 Redirige raíz a /login/
    path("", include("apps.authentication.urls")),  # rutas de login/registro
    path("", include("apps.home.urls"))             # rutas del sistema
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
