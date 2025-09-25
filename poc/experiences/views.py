# ============================================================
# poc/experiences/views.py
# ============================================================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from .models import Enterprise, Review, Comment
from .forms import SignUpForm, ReviewForm, CommentForm


# ============================================================
# Autenticación básica (signup / login / logout)
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

# ============================================================
# Gestión de publicaciones y comentarios del usuario autenticado
# ------------------------------------------------------------
@login_required(login_url="/login/")
def user_posts(request):
    """
    Lista las publicaciones (reviews y comentarios) del usuario autenticado.
    Incluye tanto las que marcó como anónimas como las públicas, ya que la autoría
    sigue siendo del usuario.
    """
    user = request.user
    user_reviews = Review.objects.filter(author=user).select_related("enterprise").order_by("-created_at")
    user_comments = Comment.objects.filter(author=user).select_related("review", "review__enterprise").order_by("-created_at")
    return render(
        request,
        "experiences/user_posts.html",
        {"user_reviews": user_reviews, "user_comments": user_comments},
    )


@login_required(login_url="/login/")
@require_POST
def delete_review(request, pk):
    """
    Elimina una review del usuario. Solo el autor puede eliminar.
    """
    review = get_object_or_404(Review, pk=pk)
    if review.author_id != request.user.id:
        return HttpResponseForbidden("No tienes permiso para eliminar esta review.")
    review.delete()
    return redirect("user_posts")


@login_required(login_url="/login/")
@require_POST
def delete_comment(request, pk):
    """
    Elimina un comentario del usuario. Solo el autor puede eliminar.
    """
    comment = get_object_or_404(Comment, pk=pk)
    if comment.author_id != request.user.id:
        return HttpResponseForbidden("No tienes permiso para eliminar este comentario.")
    comment.delete()
    return redirect("user_posts")

def health(request):
    """Endpoint de salud (health check)."""
    return HttpResponse("OK - AskMeJobs")