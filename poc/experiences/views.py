# poc/experiences/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout

from .models import Experience


# -------- Home (lista + búsqueda) --------
def home(request):
    q = request.GET.get('q', '')
    exps = Experience.objects.all()
    if q:
        exps = exps.filter(title__icontains=q) | exps.filter(company__icontains=q)
    return render(request, 'experiences/home.html', {'exps': exps, 'q': q})


# -------- Detalle --------
def detail(request, pk):
    e = get_object_or_404(Experience, pk=pk)
    return render(request, 'experiences/detail.html', {'e': e})


# -------- US1 PoC: Publicar --------
class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ["company", "title", "summary", "body"]

@login_required(login_url="/login/")
def create_experience(request):
    if request.method == "POST":
        form = ExperienceForm(request.POST)
        if form.is_valid():
            exp = form.save()
            return redirect("detail", pk=exp.pk)
    else:
        form = ExperienceForm()
    return render(request, 'experiences/new.html', {"form": form})


# -------- US5/US6 PoC: Registro / Login / Logout --------
def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, 'experiences/signup.html', {"form": form})

def signin(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")
    else:
        form = AuthenticationForm()
    return render(request, 'experiences/login.html', {"form": form})

def signout(request):
    logout(request)
    return redirect("home")