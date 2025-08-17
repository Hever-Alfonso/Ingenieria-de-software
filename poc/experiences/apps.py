# ------------------------------
# Importamos AppConfig, clase base para configurar una app de Django
# ------------------------------
from django.apps import AppConfig


# ------------------------------
# Configuración de la aplicación "experiences"
# ------------------------------
class ExperiencesConfig(AppConfig):
    # Define el tipo de campo automático por defecto para IDs
    default_auto_field = 'django.db.models.BigAutoField'
    
    # Nombre de la aplicación (debe coincidir con la carpeta del módulo)
    name = 'experiences'

    # Método que se ejecuta cuando la app está lista
    def ready(self):
        # Importamos signals para asegurarnos de que se registren
        # Esto permite que los receptores (receivers) de señales de Django
        # se activen en momentos clave (ej. post_save, pre_delete, etc.)
        from . import signals