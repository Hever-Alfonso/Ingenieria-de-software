#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys


def main():
    """
    📌 Función principal que arranca las tareas administrativas de Django.
    
    - Configura la variable de entorno para que Django sepa dónde están los settings.
    - Llama a la utilidad de línea de comandos de Django.
    - Permite ejecutar comandos como:
        python manage.py runserver     → levantar el servidor
        python manage.py makemigrations → generar migraciones
        python manage.py migrate        → aplicar migraciones
        python manage.py createsuperuser → crear un admin
    """
    # Configura por defecto el archivo de configuración de este proyecto
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'askmejobs.settings')

    try:
        # Importa el gestor de comandos de Django
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # Si Django no está instalado, lanza un error explicativo
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Ejecuta los comandos pasados desde la terminal
    execute_from_command_line(sys.argv)


# Punto de entrada del script
if __name__ == '__main__':
    main()