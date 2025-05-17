from django.shortcuts import render,redirect
from .forms import ConnexionForm, InscriptionForm
from .models import Utilisateur
# Create your views here.

#Methode pour afficher la page utilisateur
def user_home(request):
    return render(request, 'user_template/home.html')

def inscription(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            utilisateur = form.save()
            user_type = form.cleaned_data.get('user_type')
            if user_type == 'personnel':
                return redirect('admin_home')  # Mets ici le nom de ta vue/template admin
            return redirect('connexion')
    else:
        form = InscriptionForm()
    return render(request, 'user_template/inscription.html', {'form': form})
def connexion(request):
    if request.method == 'POST':
        form = ConnexionForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            mot_de_passe = form.cleaned_data['mot_de_passe']
            try:
                user = Utilisateur.objects.get(email=email, mot_de_passe=mot_de_passe)
                if hasattr(user, 'medecin'):
                    return redirect('medecin_home')
                elif hasattr(user, 'secretaire'):
                    return redirect('secretaire_home')
                elif hasattr(user, 'laborantin'):
                    return redirect('laborantin_home')
                elif hasattr(user, 'patient'):
                    return redirect('acceuil')
                else:
                    return redirect('admin_home')
            except Utilisateur.DoesNotExist:
                form.add_error(None, "Identifiants incorrects.")
    else:
        form = ConnexionForm()
    return render(request, 'user_template/connexion.html', {'form': form})


# premiere page que vois l'utilisateur
def welcome_view(request):
    return render(request, 'user_template/welcome.html')

def admin_home(request):
    return render(request, 'admin_template/home.html')