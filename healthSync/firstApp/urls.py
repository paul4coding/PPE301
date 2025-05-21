from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    
   #/store/acceuil: URL menant à la page Acceuil utilisateur
   path('home/', views.user_home, name="acceuil"),
   
   path('inscription/', views.inscription, name='inscription'),

   path('connexion/', views.connexion, name='connexion'), 

   path('welcome/', views.welcome_view, name='welcome'),
   
# Admin URL
   path('admin_home/', views.admin_home, name='admin_home'),


   path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),


   path('admin/personnels_a_valider/', views.personnels_a_valider, name='personnels_a_valider'),
    path('admin/valider_personnel/<int:user_id>/', views.valider_personnel, name='valider_personnel'),
]