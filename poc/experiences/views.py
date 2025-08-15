from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required

from .models import Experience
from .forms import ExperienceForm


# 🏠 Home
def home(request):
    q = request.GET.get("q") if request.GET.get("q") else ""
    exps = Experience.objects.filter(company__icontains=q) | Experience.objects.filter(title__icontains=q)
    return render(request, "experiences/home.html", {"exps": exps, "q": q})


# 📄 Detalle
def detail(request, pk):
    exp = get_object_or_404(Experience, pk=pk)
    return render(request, "experiences/detail.html", {"e": exp})


# ➕ Crear experiencia (requiere login)
@login_required(login_url="/login/")
def create_experience(request):
    if request.method == "POST":
        form = ExperienceForm(request.POST)
        if form.is_valid():
            exp = form.save(commit=False)
            exp.author = request.user   # 👈 se guarda el autor pero no se muestra en público
            exp.save()
            return redirect("detail", pk=exp.pk)
    else:
        form = ExperienceForm()
    return render(request, "experiences/new.html", {"form": form})


# 🔑 Registro
def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "experiences/signup.html", {"form": form})


# 🔐 Login
def signin(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")
    else:
        form = AuthenticationForm()
    return render(request, "experiences/login.html", {"form": form})


# 🚪 Logout
def signout(request):
    logout(request)
    return redirect("home")