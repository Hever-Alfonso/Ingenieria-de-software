# ============================================================
# poc/experiences/urls.py
# Enrutamiento (URLconf) de la app "experiences"
# ------------------------------------------------------------
# ¿Qué hace este archivo?
# - Define las rutas (URLs) específicas de la app.
# - Cada ruta apunta a una vista (función en views.py).
# - Se usan nombres de ruta (name=...) para poder hacer
#   reverse() o usar {% url 'nombre' %} en templates.
# ============================================================

from django.urls import path
from . import views

# ============================================================
# Lista de rutas de la aplicación
# ------------------------------------------------------------
# Nota: estas rutas se incluyen normalmente en urls.py del proyecto
# principal con algo como:
#     path('', include('experiences.urls'))
# ============================================================
urlpatterns = [
    # -------------------------
    # Página principal
    # -------------------------
    path('', views.home, name='home'),
    # Muestra lista general o bienvenida (vista home).

    # -------------------------
    # Publicaciones (Experiences)
    # -------------------------
    path('exp/<int:pk>/', views.detail, name='detail'),
    # Vista de detalle de una publicación específica (pk = primary key).

    path('new/', views.create_experience, name='new'),
    # Formulario para crear una nueva publicación/experiencia.

    # -------------------------
    # Autenticación de usuarios
    # -------------------------
    path('signup/', views.signup, name='signup'),
    # Registro de un nuevo usuario.

    path('login/', views.signin, name='login'),
    # Inicio de sesión (login).

    path('logout/', views.signout, name='logout'),
    # Cierre de sesión (logout).

    # -------------------------
    # Resúmenes por empresa
    # -------------------------
    path('companies/', views.companies_overview, name='companies_overview'),
    # Vista que muestra el listado de empresas con sus resúmenes generales.

    path('companies/<str:company>/', views.company_summary_detail, name='company_summary_detail'),
    # Vista detallada del resumen de una empresa específica.
    # <str:company> se usa para capturar el nombre de la empresa en la URL.
]