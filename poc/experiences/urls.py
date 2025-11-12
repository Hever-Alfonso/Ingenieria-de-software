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
    path('', views.index, name='index'),

    # -------------------------
    # Experiencias por empresa
    # -------------------------
    path("enterprises/<int:pk>/experiences/", views.enterprise_experiences, name="enterprise_experiences"),

    # -------------------------
    # Detalle de experiencia y comentarios
    # -------------------------
    path("reviews/<int:pk>/", views.review_detail, name="review_detail"),

    # -------------------------
    # Creación de nuevas experiencias
    # -------------------------
    path("enterprises/<int:pk>/reviews/new/", views.review_create, name="review_create"),

    # -------------------------
    # Experiencias de cada usuario
    # -------------------------
    path("me/posts/", views.user_posts, name="user_posts"),
    path("me/posts/review/<int:pk>/delete/", views.delete_review, name="delete_review"),
    path("me/posts/review/<int:pk>/edit/", views.review_edit, name="edit_review"),
    path("me/posts/comment/<int:pk>/delete/", views.delete_comment, name="delete_comment"),
    path("me/posts/comment/<int:pk>/edit/", views.comment_edit, name="edit_comment"),

    # -------------------------
    # Autenticación de usuarios
    # -------------------------
    path('signup/', views.signup, name='signup'),
    path('login/', views.signin, name='login'),
    path('logout/', views.signout, name='logout'),

    # -------------------------
    # Ruta de verificación (Health Check)
    # -------------------------
    path('health/', views.health, name='health'),
    # Endpoint simple de verificación para comprobar
    # que la aplicación responde correctamente (útil en pruebas o despliegues).
]