"""
Django settings for askmejobs project.

Generado automáticamente por 'django-admin startproject'.
Aquí se configuran las opciones principales del proyecto.
"""

from pathlib import Path
import os

# Config de AI Gemini
GENAI_CONFIG = {
    # Max tokens del output
    "max_output_tokens": 600,
    # Temperatura baja para resúmenes consistentes
    "temperature": 0.2,
    # Desactivar thinking
    "thinking_config": {"thinking_budget": 0},
}

# ========================
# 🔹 RUTA BASE DEL PROYECTO
# ========================
# BASE_DIR nos permite construir rutas relativas dentro del proyecto.
BASE_DIR = Path(__file__).resolve().parent.parent


# ========================
# 🔹 SEGURIDAD
# ========================
# ⚠️ SECRET_KEY: Clave que Django usa internamente para firmar cookies y tokens.
# Nunca debe compartirse en producción.
SECRET_KEY = 'django-insecure-dzz!v$-%-y8l!l$8fiv*786)*b5i92tcm4vbhgy4i4ry@*qij&'

# DEBUG=True: útil en desarrollo porque muestra errores detallados.
# En producción debe ponerse en False.
DEBUG = True

# ALLOWED_HOSTS: lista de dominios/hosts permitidos para servir la app.
# De momento está vacío porque solo usamos localhost.
ALLOWED_HOSTS = []


# ========================
# 🔹 APLICACIONES INSTALADAS
# ========================
INSTALLED_APPS = [
    'django.contrib.admin',          # Panel de administración de Django
    'django.contrib.auth',           # Sistema de autenticación
    'django.contrib.contenttypes',   # Soporte para tipos de contenido
    'django.contrib.sessions',       # Manejo de sesiones de usuarios
    'django.contrib.messages',       # Sistema de mensajes temporales
    'django.contrib.staticfiles',    # Manejo de archivos estáticos (CSS, JS, etc.)
    
    # 👉 Nuestra app principal donde están los modelos, views y templates
    #'experiences',
    'experiences.apps.ExperiencesConfig',  # Asegura que el método ready() se ejecute
]


# ========================
# 🔹 MIDDLEWARE
# ========================
# Son "capas" que procesan la petición antes/después de llegar a las vistas.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',      # Protección contra ataques CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Manejo de autenticación
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ========================
# 🔹 CONFIGURACIÓN DE RUTAS
# ========================
ROOT_URLCONF = 'askmejobs.urls'  # Archivo principal de URLs del proyecto


# ========================
# 🔹 TEMPLATES
# ========================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],          # Podríamos agregar aquí carpetas de templates globales
        'APP_DIRS': True,    # Busca automáticamente templates dentro de cada app
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# ========================
# 🔹 WSGI (despliegue en servidores web)
# ========================
WSGI_APPLICATION = 'askmejobs.wsgi.application'


# ========================
# 🔹 BASE DE DATOS
# ========================
# Por defecto usamos SQLite (archivo local db.sqlite3).
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ========================
# 🔹 VALIDACIÓN DE CONTRASEÑAS
# ========================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ========================
# 🔹 INTERNACIONALIZACIÓN
# ========================
LANGUAGE_CODE = 'en-us'   # Podríamos cambiarlo a 'es' para español
TIME_ZONE = 'UTC'         # Ajustar a la zona horaria local si es necesario
USE_I18N = True
USE_TZ = True


# ========================
# 🔹 ARCHIVOS ESTÁTICOS
# ========================
STATIC_URL = 'static/'  # Carpeta donde estarán CSS, JS e imágenes


# ========================
# 🔹 PRIMARY KEYS POR DEFECTO
# ========================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'