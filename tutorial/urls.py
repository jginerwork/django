from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # 1. Panel de administración (opcional, pero útil)
    path("admin/", admin.site.urls),

    # 2. Incluimos las URLs de tu app 'snippets'
    # Como snippets/urls.py ya tiene los routers, esto generará rutas como /snippets/, /users/, etc.
    path("", include("snippets.urls")),

    # 3. Login global de DRF
    # Al ponerlo aquí (en la raíz), el namespace 'rest_framework' se registra globalmente.
    # Esto soluciona el error de la plantilla de login.
    path("api-auth/", include("rest_framework.urls")),
]