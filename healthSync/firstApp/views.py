from django.shortcuts import render, redirect, get_object_or_404
from .forms import ConnexionForm, InscriptionForm
from .models import Utilisateur, Patient, Laborantin, Medecin, Secretaire
from django.views.decorators.http import require_POST
from django.contrib import messages
# Fonction utilitaire pour déterminer le rôle d'un utilisateur
def get_user_role(user):
    if hasattr(user, 'medecin'):
        return "medecin"
    elif hasattr(user, 'secretaire'):
        return "secretaire"
    elif hasattr(user, 'laborantin'):
        return "laborantin"
    elif hasattr(user, 'patient'):
        return "patient"
    return None

# Les listes de rôles pour les menus dynamiques (à réutiliser dans chaque vue concernée)
ROLES_PAGES_ACCES = ['patient', 'secretaire', 'medecin']
ROLES_SUPPORT = ['patient', 'secretaire', 'laborantin']

def user_home(request):
    user_id = request.session.get('user_id')
    user = None
    role = None
    if user_id:
        user = Utilisateur.objects.get(id=user_id)
        role = get_user_role(user)
    return render(request, 'user_template/home.html', {
        'user': user,
        'role': role,
        'roles_pages_acces': ROLES_PAGES_ACCES,
        'roles_support': ROLES_SUPPORT,
    })

def inscription(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST, request.FILES)
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
                Patient.objects.create(
                    **user_data,
                    numero_carte_identite=form.cleaned_data['numero_carte_identite'],
                    is_validated=True  # Patient validé directement
                )
            elif user_type == 'personnel':
                if personnel_role == 'medecin':
                    Medecin.objects.create(**user_data, specialite=specialite, is_validated=False)
                elif personnel_role == 'laborantin':
                    Laborantin.objects.create(**user_data, is_validated=False)
                elif personnel_role == 'secretaire':
                    Secretaire.objects.create(**user_data, is_validated=False)
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
                # Vérification de la validation pour le personnel de santé
                if (hasattr(user, 'medecin') or hasattr(user, 'secretaire') or hasattr(user, 'laborantin')) and not user.is_validated:
                    form.add_error(None, "Votre compte doit être validé par l'administrateur avant de pouvoir vous connecter.")
                    return render(request, 'user_template/connexion.html', {'form': form})
                request.session['user_id'] = user.id
                # Redirection selon le type d'utilisateur
                if hasattr(user, 'admin'):
                    return redirect('admin_dashboard')
                elif hasattr(user, 'medecin'):
                    return redirect('admin_home')
                elif hasattr(user, 'secretaire'):
                    return redirect('admin_home')
                elif hasattr(user, 'laborantin'):
                    return redirect('admin_home')
                elif hasattr(user, 'patient'):
                    return redirect('admin_home')
                else:
                    return redirect('admin_home')
            except Utilisateur.DoesNotExist:
                form.add_error(None, "Identifiants incorrects.")
    else:
        form = ConnexionForm()
    return render(request, 'user_template/connexion.html', {'form': form})

# premiere page que voit l'utilisateur
def welcome_view(request):
    user_id = request.session.get('user_id')
    user = None
    role = None
    if user_id:
        user = Utilisateur.objects.get(id=user_id)
        role = get_user_role(user)
    return render(request, 'user_template/welcome.html', {
        'user': user,
        'role': role,
        'roles_pages_acces': ROLES_PAGES_ACCES,
        'roles_support': ROLES_SUPPORT,
    })

def admin_home(request):
    user_id = request.session.get('user_id')
    user = None
    role = None
    if user_id:
        user = Utilisateur.objects.get(id=user_id)
        role = get_user_role(user)
        nb_medecins = Medecin.objects.count()

    return render(request, 'admin_template/home.html', {
        'user': user,
        'role': role,
        'roles_pages_acces': ROLES_PAGES_ACCES,
        'roles_support': ROLES_SUPPORT,
    })

# Si tu as secretaire_home, laborantin_home, etc., ajoute le calcul et le passage des variables comme ci-dessus !

    return render(request, 'admin_template/home.html', {'user': user})


def admin_dashboard(request):
    user_id = request.session.get('user_id')
    user = None
    if user_id:
        user = Utilisateur.objects.get(id=user_id)
    # Liste des personnels de santé non validés (patients exclus)
    medecins = Medecin.objects.filter(is_validated=False)
    laborantins = Laborantin.objects.filter(is_validated=False)
    secretaires = Secretaire.objects.filter(is_validated=False)
    return render(request, 'admin_template/admin_dashboard.html', {
        'user': user,
        'medecins': medecins,
        'laborantins': laborantins,
        'secretaires': secretaires,
    })


def personnels_a_valider(request):
    # Liste tous les personnels de santé non validés
    medecins = Medecin.objects.filter(is_validated=False)
    laborantins = Laborantin.objects.filter(is_validated=False)
    secretaires = Secretaire.objects.filter(is_validated=False)
    return render(request, 'admin_template/personnels_a_valider.html', {
        'medecins': medecins,
        'laborantins': laborantins,
        'secretaires': secretaires,
    })


@require_POST
def valider_personnel(request, user_id):
    user = get_object_or_404(Utilisateur, id=user_id)
    user.is_validated = True
    user.save()
    messages.success(request, f"{user.prenom} {user.nom} autorisé avec succès !")
    return redirect('admin_dashboard')

