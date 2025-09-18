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

from .models import Enterprise, Review, Comment
from .forms import SignUpForm, ReviewForm


# ============================================================
# 🔹 Autenticación básica (signup / login / logout)
# ------------------------------------------------------------
# Vistas sencillas con formularios estándar de Django.
# ============================================================

def signup(request):
    """
    Registro de usuarios nuevos.
    - GET: muestra formulario.
    - POST: valida, crea usuario, hace login y redirige a index.
    """
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("index")
    else:
        form = SignUpForm()
    return render(request, "experiences/signup.html", {"form": form})


def signin(request):
    """
    Inicio de sesión.
    - GET: muestra formulario.
    - POST: valida credenciales y redirige a index.
    """
    form = AuthenticationForm(data=request.POST or None)
    for f in form.fields.values():
        existing = f.widget.attrs.get("class", "")
        f.widget.attrs["class"] = (existing + " form-control").strip()
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect("index")
    return render(request, "experiences/login.html", {"form": form})


def signout(request):
    """Cierra sesión y envía al login."""
    logout(request)
    return redirect("login")


# ============================================================
# 🔹 Publicaciones (listado, detalle, creación)
# ============================================================

def index(request):
    q = (request.GET.get("q") or "").strip()
    qs = Enterprise.objects.all()
    if q:
        qs = qs.filter(name__icontains=q)
    qs = qs.order_by("name")
    return render(request, "experiences/index.html", {"q": q, "qs": qs})

def enterprise_experiences(request, pk):
    enterprise = get_object_or_404(Enterprise, pk=pk)
    # Trae las reviews más recientes con su autor
    reviews = enterprise.reviews.select_related("author").order_by("-created_at")
    return render(
        request,
        "experiences/enterprise_experiences.html",
        {"enterprise": enterprise, "reviews": reviews},
    )

def review_detail(request, pk):
    review = get_object_or_404(Review, pk=pk)
    return render(request, "experiences/review_detail.html", {"review": review})

# ============================================================
# Creación de nuevas reviews
# ------------------------------------------------------------
@login_required(login_url="/login/")
def review_create(request, pk):
    enterprise = get_object_or_404(Enterprise, pk=pk)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.enterprise = enterprise
            review.author = request.user
            review.save()
            return redirect("review_detail", pk=review.pk)
    else:
        form = ReviewForm()

    return render(request, "experiences/review_create.html", {"enterprise": enterprise, "form": form})

'''
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
'''

def health(request):
    """Endpoint de salud (health check)."""
    return HttpResponse("OK - AskMeJobs")