<div align="center">
  <h1>AskMeJobs · Plataforma de Experiencias Laborales (PoC)</h1>
  <p><strong>Proyecto académico</strong> para la asignatura de Ingeniería de Software.</p>
  <p>Aplicación web construida con <strong>Django</strong> que permite publicar y analizar experiencias laborales sobre empresas. Incorpora <strong>resúmenes generados por IA (Gemini)</strong> para sintetizar percepciones colectivas.</p>
  <img alt="Django" src="https://img.shields.io/badge/Django-5.x-0C4B33?logo=django&logoColor=white"> <img alt="Python" src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white"> <img alt="Status" src="https://img.shields.io/badge/Estado-PoC-blue">
</div>


## 1. Objetivo y alcance
Crear una plataforma donde candidatos y empleados compartan experiencias (reviews) sobre empresas. La PoC se enfoca en: autenticación básica, publicación anónima opcional, comentarios, métricas agregadas y resúmenes automatizados.


## 2. Funcionalidades
| Funcionalidad | Descripción | Estado |
|---------------|-------------|--------|
| Registro / Login | Autenticación con formularios Django | ✅ |
| Crear review | Reseñas con rating 1–5 + anonimato | ✅ |
| Comentar review | Comentarios con anonimato | ✅ |
| Listar empresas | Búsqueda + métricas | ✅ |
| Resumen IA | Texto sintetizado por Gemini | ✅ |
| Panel usuario | Eliminar propias reviews/comments | ✅ |
| Admin Django | Gestión de entidades | ✅ |
| Health check | `/health/` | ✅ |


## 3. Arquitectura y estructura
```
poc/
├── askmejobs/
│   ├── settings.py        # Configuración global (GENAI_CONFIG, apps, DB)
│   ├── urls.py            # Enrutamiento raíz
│   └── wsgi.py / asgi.py  # Entrada servidor
├── experiences/
│   ├── models/            # Enterprise, Review, Comment
│   ├── views.py           # Lógica de interacción
│   ├── forms.py           # Formularios y validaciones
│   ├── services.py        # Integración Gemini
│   ├── signals.py         # Dispara actualización de resumen
│   ├── urls.py            # Rutas de la app
│   ├── admin.py           # Registro en admin
│   ├── templates/         # UI (Bootstrap modo oscuro)
│   └── tests.py           # Placeholder pruebas
└── Pipfile                # Dependencias (django)
```

## 4. Modelos de datos
### Enterprise
| Campo | Tipo | Notas |
|-------|------|-------|
| name | Char(unique) | Indexado y único |
| AI_summary | Text | Resumen IA persistido |
| reviews_count (prop.) | int | Conteo dinámico |
| average_rating (prop.) | float | Promedio (0 si vacío) |

### Review
| Campo | Tipo | Notas |
|-------|------|-------|
| enterprise | FK Enterprise | Cascade delete |
| author | FK User (nullable) | SET_NULL para no romper integridad |
| title | Char(160) | — |
| body | Text | — |
| rating | SmallInt 1–5 | Validado en formulario |
| anonymous | Bool | Oculta autor |
| created_at | DateTime | auto_now_add |
| display_author (prop.) | str | “anónimo” si flag |

### Comment
| Campo | Tipo | Notas |
|-------|------|-------|
| review | FK Review | Cascade delete |
| author | FK User (nullable) | — |
| text | Text | — |
| anonymous | Bool | — |
| created_at / updated_at | DateTime | Índice por fecha |
| display_author (prop.) | str | — |

Relaciones: Enterprise 1—N Review, Review 1—N Comment.


## 5. Módulos y responsabilidades
| Módulo | Rol | Notas |
|--------|-----|-------|
| settings.py | Configuración | GENAI_CONFIG, apps, DB SQLite |
| models/ | Dominio | Propiedades derivadas para métricas |
| forms.py | Validación y UX | Añade clases Bootstrap, valida rating |
| views.py | Controlador | Flujos auth + CRUD parcial |
| services.py | IA / integración | Construye corpus + prompt + llamada Gemini |
| signals.py | Reactividad | Actualiza resumen tras cambios |
| admin.py | Backoffice | Listados, filtros y search |
| templates/ | UI | Composición con base.html |

## 6. Flujo de generación IA
1. Se crea/borra una review.
2. Señal `post_save` / `post_delete` dispara función diferida con `transaction.on_commit`.
3. `build_corpus()` concatena reviews.
4. `build_prompt()` genera instrucciones claras en español.
5. Gemini produce un resumen (texto plano ~8–10 frases).
6. Se guarda en `Enterprise.AI_summary` o mensaje fallback.

Errores: se capturan y se deja un mensaje seguro (no explota la vista principal).

## 7. Rutas (URLs)
| Ruta | Nombre | Descripción |
|------|--------|-------------|
| `/` | index | Empresas + buscador |
| `/enterprises/<id>/experiences/` | enterprise_experiences | Reviews + resumen IA |
| `/enterprises/<id>/reviews/new/` | review_create | Crear review (login) |
| `/reviews/<id>/` | review_detail | Detalle + comentar |
| `/me/posts/` | user_posts | Panel del usuario |
| `/me/posts/review/<id>/delete/` | delete_review | Eliminar review propia |
| `/me/posts/comment/<id>/delete/` | delete_comment | Eliminar comentario propio |
| `/signup/` | signup | Registro |
| `/login/` | login | Inicio sesión |
| `/logout/` | logout | Salir |
| `/health/` | health | Health check |
| `/admin/` | — | Admin Django |

## 8. Formularios
| Form | Modelo | Particularidades |
|------|--------|-----------------|
| SignUpForm | User | Email requerido + estilos |
| ReviewForm | Review | Validación explícita rating 1-5|
| CommentForm | Comment | Soporta anonimato |

## 9. Templates y UX
- Bootstrap 5 con `base.html`.
- Navegación fija superior con estado de sesión.
- Cards para empresas y reviews; badges para métricas.
- Formularios con clases inyectadas en `__init__` de los formularios.
- Modal reutilizable para confirmación de eliminaciones.

## 10. Variables de entorno
| Variable | Obligatoria | Descripción |
|----------|-------------|-------------|
| GEMINI_API_KEY | Sí | Clave de acceso a Gemini |
| GEMINI_MODEL | Sí | Modelo a usar (ej: gemini-2.5-flash) |

## 11. Ejecución de la aplicación

### Requisitos previos
- **Python 3.10+**
- **pip** instalado
- **pipenv** instalado (`pip install pipenv`)
- Archivo .env con claves `GEMINI_API_KEY` y `GEMINI_MODEL`, esta ultima puede ser: gemini-2.5-flash

### Pasos de instalación y ejecución

1. **Clonar el repositorio**
    ```bash
    git clone https://github.com/Hever-Alfonso/Ingenieria-de-software
    cd poc
    ```

2. **Instalar dependencias**

    ```
    bash
    pipenv install
    ```

3. **Inicializar la base de datos (no incluida en el repo)**

    ```bash
    pipenv run python manage.py makemigrations
    pipenv run python manage.py migrate
    ```

4. **Ejecutar el servidor de desarrollo**

    ```bash
    pipenv run python manage.py runserver
    ```

5. **Acceder a la aplicación**

   * App principal: [http://localhost:8000/](http://localhost:8000/)
   * Panel admin: [http://localhost:8000/admin/](http://localhost:8000/admin/)

### Comandos adicionales útiles

* Crear superusuario para el panel de administración:

  ```bash
  pipenv run python manage.py createsuperuser
  ```


---
<sub>Última actualización: Sept 2025</sub>
