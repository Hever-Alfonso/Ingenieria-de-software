from django.shortcuts import render, get_object_or_404
from .models import Experience

def home(request):
    q = request.GET.get('q', '')
    exps = Experience.objects.all()
    if q:
        exps = exps.filter(title__icontains=q) | exps.filter(company__icontains=q)
    return render(request, 'experiences/home.html', {'exps': exps, 'q': q})

def detail(request, pk):
    e = get_object_or_404(Experience, pk=pk)
    return render(request, 'experiences/detail.html', {'e': e})