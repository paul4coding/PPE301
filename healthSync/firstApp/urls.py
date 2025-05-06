from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    
   #/store/acceuil: URL menant à la page Acceuil utilisateur
   path('home/', views.user_home, name="acceuil"),
   
   path('inscription/', views.inscription, name='inscription'),

   path('connexion/', views.connexion, name='connexion'), 

   path('welcome/', views.welcome_view, name='welcome'),
    
]