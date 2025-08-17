# ============================================================
# poc/experiences/views.py
# Vistas de la app: publicación/listado, detalle, auth y resúmenes
# ------------------------------------------------------------
# Ideas clave:
# - Generamos un RESUMEN tipo insight por empresa a partir de
#   publicaciones y comentarios (sin dependencias externas).
# - Agrupamos variantes de marca (p.ej. "Claro", "Claro Colombia",
#   "Claro S.A.S.") para que cuenten como la misma empresa.
# - Cacheamos el resultado en CompanySummary y lo refrescamos
#   cuando cambian los datos.
# ============================================================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponse

from .models import Experience, CompanySummary, Comment
from .forms import ExperienceForm, CommentForm


# ============================================================
# 🔹 Utilidades para el resumen por empresa (helpers)
# ------------------------------------------------------------
# _norm: normaliza el nombre de la empresa para agrupar variantes.
# _build_corpus: construye un gran texto (posts + comentarios).
# _insight_summary: transforma palabras frecuentes en una frase.
# _ensure_company_summary: calcula/actualiza y devuelve CompanySummary.
# ============================================================

def _norm(s: str) -> str:
    """
    Normaliza variantes de marca para agruparlas bajo el mismo "núcleo".
    Ejemplos:
      "Claro Colombia" -> "claro"
      "Claro S.A.S."   -> "claro"
    """
    return (s or "").strip().lower()\
        .replace(" s.a.s.", "").replace(" s.a.", "").replace(" colombia", "")


def _build_corpus(company: str) -> tuple[str, int, int]:
    """
    Une publicaciones y comentarios de la marca 'company' y sus variantes.
    Devuelve:
      - corpus (str): texto concatenado de títulos, resúmenes, cuerpos y comentarios
      - n_posts (int): número de publicaciones usadas
      - n_comments (int): número de comentarios usados
    """
    core = _norm(company)

    # Publicaciones donde el nombre contiene la cadena original o el "núcleo"
    posts = (Experience.objects.filter(company__icontains=company) |
             Experience.objects.filter(company__icontains=core))

    # Comentarios de esas publicaciones (mismo criterio)
    comments = (Comment.objects.filter(experience__company__icontains=company) |
                Comment.objects.filter(experience__company__icontains=core))

    # Armamos el corpus concatenando campos relevantes
    post_texts = [f"{p.title}\n{p.summary}\n{p.body}" for p in posts]
    comment_texts = [c.text for c in comments]
    corpus = "\n".join(post_texts + comment_texts).strip()

    return corpus, posts.count(), comments.count()


def _insight_summary(text: str, company: str) -> str:
    """
    Convierte palabras más frecuentes en una frase-resumen humana (en español).
    - Tokeniza.
    - Filtra stopwords.
    - Toma top-k palabras más repetidas.
    - Redacta 1 frase natural con esas palabras clave.
    """
    import re
    from collections import Counter

    # Tokenización simple: palabras de 3+ letras, en minúsculas
    words = re.findall(r"[a-zA-ZáéíóúÁÉÍÓÚñÑ]{3,}", (text or "").lower())

    # Stopwords mínimas en español (ajustable)
    stop = {
        "para","por","con","las","los","una","unos","unas","que","como","muy","pero",
        "este","esta","esto","esa","ese","son","del","de","la","el","y","o","en","un",
        "se","al","más","mas","sus","sobre","sin","a","es","hay","ser","fue","está",
        "estan","están","estaba","estaban","solo","solo","tambien","también","ya",
        "lo","le","les","nos","me","mi","tu","su","si","sí","no"
    }

    # Filtrar palabras vacías
    keywords = [w for w in words if w not in stop]
    if not keywords:
        return f"No hay suficiente información para generar un resumen sobre {company}."

    # Palabras más frecuentes (hasta 6 para tener material)
    common = [w for w, _ in Counter(keywords).most_common(6)]

    # Seleccionamos hasta 5 para redactar
    top = common[:5]
    if len(top) == 1:
        joined = top[0]
        return f"Los usuarios hablan principalmente de {joined} en {company}."
    elif len(top) == 2:
        joined = " y ".join(top)
        return f"En general, los usuarios resaltan {joined} en {company}."
    else:
        joined = ", ".join(top[:-1]) + f" y {top[-1]}"
        return f"En general, los usuarios mencionan con mayor frecuencia {joined} en {company}."


def _ensure_company_summary(company: str) -> CompanySummary:
    """
    Calcula (o refresca) el resumen y métricas de 'company',
    persiste en CompanySummary y devuelve el objeto actualizado.
    """
    corpus, n_posts, n_comments = _build_corpus(company)

    text = (
        f"No hay suficiente información para generar un resumen sobre {company}."
        if not corpus else _insight_summary(corpus, company)
    )

    obj, _ = CompanySummary.objects.update_or_create(
        company=company,
        defaults={
            "summary": text,
            "total_posts": n_posts,
            "total_comments": n_comments,
            "last_computed": timezone.now(),
        }
    )
    return obj


# ============================================================
# 🔹 Autenticación básica (signup / login / logout)
# ------------------------------------------------------------
# Vistas sencillas con formularios estándar de Django.
# ============================================================

def signup(request):
    """
    Registro de usuarios nuevos.
    - GET: muestra formulario.
    - POST: valida, crea usuario, hace login y redirige a home.
    """
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        # Pequeño estilizado para inputs (Bootstrap)
        for f in form.fields.values():
            existing = f.widget.attrs.get("class", "")
            f.widget.attrs["class"] = (existing + " form-control").strip()
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()
        for f in form.fields.values():
            existing = f.widget.attrs.get("class", "")
            f.widget.attrs["class"] = (existing + " form-control").strip()
    return render(request, "experiences/signup.html", {"form": form})


def signin(request):
    """
    Inicio de sesión.
    - GET: muestra formulario.
    - POST: valida credenciales y redirige a home.
    """
    form = AuthenticationForm(data=request.POST or None)
    for f in form.fields.values():
        existing = f.widget.attrs.get("class", "")
        f.widget.attrs["class"] = (existing + " form-control").strip()
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect("home")
    return render(request, "experiences/login.html", {"form": form})


def signout(request):
    """Cierra sesión y envía al login."""
    logout(request)
    return redirect("login")


# ============================================================
# 🔹 Publicaciones (listado, detalle, creación)
# ============================================================

def home(request):
    """
    Listado de publicaciones con búsqueda simple (por empresa o título).
    - Recibe ?q= para filtrar.
    - Ordena de más reciente a más antiguo.
    """
    q = request.GET.get("q") or ""
    qs = (Experience.objects.filter(company__icontains=q) |
          Experience.objects.filter(title__icontains=q))
    experiences = qs.order_by("-created_at")
    return render(request, "experiences/home.html", {"experiences": experiences, "q": q})


def detail(request, pk):
    """
    Detalle de una publicación y sus comentarios.
    - GET: muestra publicación + comentarios + form (si logueado).
    - POST: crea un comentario y recarga el detalle.
    """
    e = get_object_or_404(Experience, pk=pk)

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("login")
        cform = CommentForm(request.POST)
        for f in cform.fields.values():
            existing = f.widget.attrs.get("class", "")
            f.widget.attrs["class"] = (existing + " form-control").strip()
        if cform.is_valid():
            c = cform.save(commit=False)
            c.experience = e
            c.author = request.user
            c.save()
            # Nota: Las señales recalculan el resumen automáticamente.
            return redirect("detail", pk=e.pk)
    else:
        cform = CommentForm()
        for f in cform.fields.values():
            existing = f.widget.attrs.get("class", "")
            f.widget.attrs["class"] = (existing + " form-control").strip()

    return render(request, "experiences/detail.html", {"e": e, "cform": cform})


@login_required(login_url="/login/")
def create_experience(request):
    """
    Crea una nueva publicación (Experience).
    - GET: muestra formulario.
    - POST: valida/guarda, asegura resumen fresco y redirige al detalle.
    """
    if request.method == "POST":
        form = ExperienceForm(request.POST)
        for f in form.fields.values():
            existing = f.widget.attrs.get("class", "")
            f.widget.attrs["class"] = (existing + " form-control").strip()
        if form.is_valid():
            exp = form.save(commit=False)
            exp.author = request.user
            exp.save()  # Señales recalculan automáticamente
            _ensure_company_summary(exp.company)  # Garantiza resumen “fresco”
            return redirect("detail", pk=exp.pk)
    else:
        form = ExperienceForm()
        for f in form.fields.values():
            existing = f.widget.attrs.get("class", "")
            f.widget.attrs["class"] = (existing + " form-control").strip()
    return render(request, "experiences/new.html", {"form": form})


# ============================================================
# 🔹 Resúmenes por empresa (overview + detalle + health)
# ------------------------------------------------------------
# companies_overview:
#   - Lista todas las empresas registradas en CompanySummary
#     con su resumen generado, en orden alfabético.
#
# company_summary_detail:
#   - Muestra el resumen específico de una empresa.
#   - Antes de renderizar, recalcula/asegura que el resumen esté actualizado.
#
# health:
#   - Endpoint simple de verificación (health check).
#   - Responde "OK - AskMeJobs" si el servicio está activo.
# ============================================================

def companies_overview(request):
    """Lista de resúmenes por empresa (ordenadas alfabéticamente)."""
    companies = CompanySummary.objects.order_by("company")
    return render(request, "experiences/companies_overview.html", {"companies": companies})


def company_summary_detail(request, company):
    """Vista de detalle del resumen de una empresa específica."""
    obj = _ensure_company_summary(company)
    return render(request, "experiences/company_summary_detail.html", {"summary": obj})


def health(request):
    """Endpoint de salud (health check)."""
    return HttpResponse("OK - AskMeJobs")