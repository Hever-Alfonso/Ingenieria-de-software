from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import Experience
from .forms import ExperienceForm

# =======================
# 🔹 REGISTRO DE USUARIO
# =======================
def signup(request):
    """
    Vista para crear una nueva cuenta de usuario.
    - Si es POST: procesa el formulario de registro.
    - Si es GET: muestra el formulario vacío.
    - Se aplican clases de Bootstrap a los campos del formulario.
    - Si es válido, se crea el usuario y se inicia sesión automáticamente.
    """
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        # Agregar clases de Bootstrap a los campos
        for f in form.fields.values():
            existing = f.widget.attrs.get("class", "")
            f.widget.attrs["class"] = (existing + " form-control").strip()

        if form.is_valid():
            user = form.save()
            login(request, user)  # inicia sesión automáticamente
            return redirect("home")
    else:
        form = UserCreationForm()
        for f in form.fields.values():
            existing = f.widget.attrs.get("class", "")
            f.widget.attrs["class"] = (existing + " form-control").strip()

    return render(request, "experiences/signup.html", {"form": form})


# =======================
# 🔹 LOGIN DE USUARIO
# =======================
def signin(request):
    """
    Vista para iniciar sesión de usuario.
    - Si es POST: procesa credenciales.
    - Si es GET: muestra el formulario vacío.
    - Se aplican clases de Bootstrap a los campos del formulario.
    - Si las credenciales son correctas, inicia sesión y redirige al home.
    """
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        for f in form.fields.values():
            existing = f.widget.attrs.get("class", "")
            f.widget.attrs["class"] = (existing + " form-control").strip()

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")
    else:
        form = AuthenticationForm()
        for f in form.fields.values():
            existing = f.widget.attrs.get("class", "")
            f.widget.attrs["class"] = (existing + " form-control").strip()

    return render(request, "experiences/login.html", {"form": form})


# =======================
# 🔹 LOGOUT DE USUARIO
# =======================
def signout(request):
    """
    Vista para cerrar sesión del usuario actual.
    Luego redirige al home.
    """
    logout(request)
    return redirect("home")


# =======================
# 🔹 HOME
# =======================
def home(request):
    """
    Vista principal de la app.
    - Permite listar experiencias.
    - Incluye búsqueda por empresa o título usando query param 'q'.
    """
    q = request.GET.get("q") if request.GET.get("q") else ""
    experiences = Experience.objects.filter(company__icontains=q) | Experience.objects.filter(title__icontains=q)
    return render(request, "experiences/home.html", {"experiences": experiences})


# =======================
# 🔹 DETALLE DE EXPERIENCIA
# =======================
def detail(request, pk):
    """
    Vista para mostrar el detalle de una experiencia.
    Busca la experiencia por su primary key (pk).
    Si no existe, devuelve 404.
    """
    e = get_object_or_404(Experience, pk=pk)
    return render(request, "experiences/detail.html", {"e": e})


# =======================
# 🔹 CREAR EXPERIENCIA
# =======================
@login_required(login_url="/login/")
def create_experience(request):
    """
    Vista para crear una nueva experiencia.
    - Requiere que el usuario esté autenticado.
    - Si es POST: procesa el formulario, asigna autor y guarda.
    - Si es GET: muestra el formulario vacío.
    """
    if request.method == "POST":
        form = ExperienceForm(request.POST)
        for f in form.fields.values():
            existing = f.widget.attrs.get("class", "")
            f.widget.attrs["class"] = (existing + " form-control").strip()

        if form.is_valid():
            exp = form.save(commit=False)  # no guarda aún
            exp.author = request.user      # asigna autor al usuario logueado
            exp.save()
            return redirect("detail", pk=exp.pk)
    else:
        form = ExperienceForm()
        for f in form.fields.values():
            existing = f.widget.attrs.get("class", "")
            f.widget.attrs["class"] = (existing + " form-control").strip()

    return render(request, "experiences/new.html", {"form": form})