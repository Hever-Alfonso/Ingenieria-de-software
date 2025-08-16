# poc/experiences/urls.py
from django.urls import path
from . import views

# =========================
# 🔹 RUTAS DE LA APLICACIÓN
# =========================
# Aquí definimos las URLs específicas de la app "experiences".
# Cada ruta apunta a una vista en views.py y recibe un 'name' para poder
# ser llamada desde templates con {% url 'name' %}.
urlpatterns = [
    # 🏠 Página principal con todas las publicaciones
    path('', views.home, name='home'),

    # 🔎 Ver detalle de una experiencia en específico (por ID)
    path('exp/<int:pk>/', views.detail, name='detail'),

    # ➕ Crear nueva experiencia (requiere login)
    path('new/', views.create_experience, name='new'),

    # 👤 Registro de usuario
    path('signup/', views.signup, name='signup'),

    # 🔑 Inicio de sesión
    path('login/', views.signin, name='login'),

    # 🚪 Cerrar sesión
    path('logout/', views.signout, name='logout'),
]