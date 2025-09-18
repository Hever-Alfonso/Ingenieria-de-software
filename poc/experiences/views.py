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
from .forms import SignUpForm, ReviewForm, CommentForm


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
    review = get_object_or_404(
        Review.objects.select_related("enterprise", "author"), pk=pk
    )

    comments = review.comments.select_related("author").order_by("-created_at")

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect(f"/login/?next=/reviews/{pk}/")

        form = CommentForm(request.POST)
        if form.is_valid():
            c = form.save(commit=False)
            c.review = review
            c.author = request.user
            c.save()
            return redirect("review_detail", pk=review.pk)
    else:
        form = CommentForm()

    return render(
        request,
        "experiences/review_detail.html",
        {"review": review, "comments": comments, "form": form},
    )
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

def health(request):
    """Endpoint de salud (health check)."""
    return HttpResponse("OK - AskMeJobs")