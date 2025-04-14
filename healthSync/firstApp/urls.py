from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    
   #/store/acceuil: URL menant à la page Acceuil utilisateur
   path('home/', views.user_home, name="acceuil"),    
    
]