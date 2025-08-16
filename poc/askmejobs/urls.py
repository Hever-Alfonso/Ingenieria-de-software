from django.contrib import admin
from django.urls import path, include

# 📌 urlpatterns es la lista principal de rutas de todo el proyecto.
# Django revisa estas rutas en orden y redirige a la vista correspondiente.
urlpatterns = [
    # ✅ Ruta para el panel de administración de Django
    #    Se accede desde /admin/
    path('admin/', admin.site.urls),

    # ✅ Incluimos las rutas de la app "experiences"
    #    El include trae todas las urls definidas en experiences/urls.py
    #    Como el prefijo es '', significa que esas rutas serán la raíz del sitio.
    path('', include('experiences.urls')),
]