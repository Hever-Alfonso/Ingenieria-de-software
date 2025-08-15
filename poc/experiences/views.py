from django.http import HttpResponse

def home(request):
    return HttpResponse("AskMeJobs PoC — wiring OK ✅")