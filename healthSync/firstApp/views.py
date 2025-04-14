from django.shortcuts import render

# Create your views here.

#Methode pour afficher la page utilisateur
def user_home(request):
    return render(request, 'user_template/home.html')
