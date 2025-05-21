from django.shortcuts import render,redirect
from .forms import ConnexionForm, InscriptionForm
from .models import Utilisateur,Patient, Laborantin, Medecin, Secretaire
# Create your views here.

#Methode pour afficher la page utilisateur
def user_home(request):
    return render(request, 'user_template/home.html')

def inscription(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST, request.FILES)  # <-- Correction ici
        if form.is_valid():
            user_type = form.cleaned_data['user_type']
            personnel_role = form.cleaned_data.get('personnel_role')
            specialite = form.cleaned_data.get('specialite')
            photo = form.cleaned_data.get('photo')
            user_data = {
                'nom': form.cleaned_data['nom'],
                'prenom': form.cleaned_data['prenom'],
                'sexe': form.cleaned_data['sexe'],
                'age': form.cleaned_data['age'],
                'email': form.cleaned_data['email'],
                'mot_de_passe': form.cleaned_data['mot_de_passe'],
                'photo': photo,
            }
            if user_type == 'patient':
                Patient.objects.create(**user_data, numero_carte_identite=form.cleaned_data['numero_carte_identite'])
            elif user_type == 'personnel':
                if personnel_role == 'medecin':
                    Medecin.objects.create(**user_data, specialite=specialite)
                elif personnel_role == 'laborantin':
                    Laborantin.objects.create(**user_data)
                elif personnel_role == 'secretaire':
                    Secretaire.objects.create(**user_data)
            return redirect('welcome')
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
                # Sauvegarde l'ID utilisateur dans la session
                request.session['user_id'] = user.id
                # Redirection selon le type d'utilisateur
                if hasattr(user, 'medecin'):
                    return redirect('admin_home')
                elif hasattr(user, 'secretaire'):
                    return redirect('secretaire_home')
                elif hasattr(user, 'laborantin'):
                    return redirect('laborantin_home')
                elif hasattr(user, 'patient'):
                    return redirect('welcome')
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
    user_id = request.session.get('user_id')
    user = None
    if user_id:
        from .models import Utilisateur
        user = Utilisateur.objects.get(id=user_id)
    return render(request, 'admin_template/home.html', {'user': user})