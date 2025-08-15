from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('exp/<int:pk>/', views.detail, name='detail'),
    path('new/', views.create_experience, name='new'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.signin, name='login'),
    path('logout/', views.signout, name='logout'),
]