from django.shortcuts import render, redirect, get_object_or_404
from .forms import ConnexionForm, InscriptionForm
from .models import Utilisateur, Patient, Laborantin, Medecin, Secretaire
from django.views.decorators.http import require_POST
from django.contrib import messages

from django.db import IntegrityError

from django.contrib.auth.decorators import login_required

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




# Fonction utilitaire pour DRY (évite la répétition)
def get_admin_context(request):
    user_id = request.session.get('user_id')
    user = None
    role = None
    if user_id:
        user = Utilisateur.objects.get(id=user_id)
        # Utilise ta fonction pour déterminer le rôle :
        role = get_user_role(user)
    return {
        'user': user,
        'role': role,
        'roles_pages_acces': ROLES_PAGES_ACCES,
        'roles_support': ROLES_SUPPORT,
    }

# --- CHARTS ---
def charts_chartjs_bar(request):
    return render(request, "admin_template/html/charts-chartjs-bar.html", get_admin_context(request))
def charts_chartjs_line(request):
    return render(request, "admin_template/html/charts-chartjs-line.html", get_admin_context(request))
def charts_chartjs_pie_donut(request):
    return render(request, "admin_template/html/charts-chartjs-pie-donut.html", get_admin_context(request))
def charts_echart_bar(request):
    return render(request, "admin_template/html/charts-echart-bar.html", get_admin_context(request))
def charts_echart_line(request):
    return render(request, "admin_template/html/charts-echart-line.html", get_admin_context(request))
def charts_flot_area(request):
    return render(request, "admin_template/html/charts-flot-area.html", get_admin_context(request))
def charts_flot_line(request):
    return render(request, "admin_template/html/charts-flot-line.html", get_admin_context(request))
def charts_flot_stacked(request):
    return render(request, "admin_template/html/charts-flot-stacked.html", get_admin_context(request))
def charts_morris_area(request):
    return render(request, "admin_template/html/charts-morris-area.html", get_admin_context(request))
def charts_morris_bar(request):
    return render(request, "admin_template/html/charts-morris-bar.html", get_admin_context(request))
def charts_morris_line(request):
    return render(request, "admin_template/html/charts-morris-line.html", get_admin_context(request))
def charts_morris_pie(request):
    return render(request, "admin_template/html/charts-morris-pie.html", get_admin_context(request))
def charts_sparkline_bar(request):
    return render(request, "admin_template/html/charts-sparkline-bar.html", get_admin_context(request))
def charts_sparkline_composite(request):
    return render(request, "admin_template/html/charts-sparkline-composite.html", get_admin_context(request))
def charts_sparkline_line(request):
    return render(request, "admin_template/html/charts-sparkline-line.html", get_admin_context(request))

# --- FORM ---
def form_elements_grid(request):
    return render(request, "admin_template/html/form-elements-grid.html", get_admin_context(request))
def form_elements_icheck(request):
    return render(request, "admin_template/html/form-elements-icheck.html", get_admin_context(request))
def form_elements_premade(request):
    return render(request, "admin_template/html/form-elements-premade.html", get_admin_context(request))
def form_elements(request):
    return render(request, "admin_template/html/form-elements.html", get_admin_context(request))
def form_validation(request):
    return render(request, "admin_template/html/form-validation.html", get_admin_context(request))
def form_wizard(request):
    return render(request, "admin_template/html/form-wizard.html", get_admin_context(request))

# --- HOSPITAL/ADMIN ---
def hos_add_doctor(request):
    return render(request, "admin_template/html/hos-add-doctor.html", get_admin_context(request))

#ajout de patient
def hos_add_patient(request):
    context = get_admin_context(request)
    if request.method == "POST":
        nom = request.POST.get("nom")
        prenom = request.POST.get("prenom")
        sexe = request.POST.get("sexe")
        age = request.POST.get("age")
        email = request.POST.get("email")
        mot_de_passe = request.POST.get("password")
        mot_de_passe2 = request.POST.get("password_confirm")
        numero_carte_identite = request.POST.get("numero_carte_identite")
        photo = request.FILES.get("photo")
        
        # Validation basique
        if mot_de_passe != mot_de_passe2:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return render(request, "admin_template/html/hos-add-patient.html", context)
        
        if Patient.objects.filter(email=email).exists():
            messages.error(request, "Cet email existe déjà.")
            return render(request, "admin_template/html/hos-add-patient.html", context)
        
        if Patient.objects.filter(numero_carte_identite=numero_carte_identite).exists():
            messages.error(request, "Ce numéro de carte d'identité existe déjà.")
            return render(request, "admin_template/html/hos-add-patient.html", context)

        try:
            patient = Patient(
                nom=nom,
                prenom=prenom,
                sexe=sexe,
                age=age,
                email=email,
                mot_de_passe=mot_de_passe,  # À chiffrer avec make_password pour une vraie app !
                numero_carte_identite=numero_carte_identite,
                photo=photo
            )
            patient.save()
            messages.success(request, "Le patient a bien été ajouté.")
            return redirect("hos_all_patients")
        except IntegrityError:
            messages.error(request, "Erreur lors de la création du patient (données uniques ?).")
            return render(request, "admin_template/html/hos-add-patient.html", context)

    return render(request, "admin_template/html/hos-add-patient.html", context)

def hos_add_payment(request):
    return render(request, "admin_template/html/hos-add-payment.html", get_admin_context(request))
def hos_all_doctors(request):
    return render(request, "admin_template/html/hos-all-doctors.html", get_admin_context(request))


def hos_all_patients(request):
    context = get_admin_context(request)
    context['patients'] = Patient.objects.all()
    return render(request, "admin_template/html/hos-all-patients.html", context)

def hos_book_appointment(request):
    return render(request, "admin_template/html/hos-book-appointment.html", get_admin_context(request))




def hos_doctor_dash(request):
    return render(request, 'admin_template/html/hos-patient-dash.html', {'patient': patient})


def hos_doctor_profile(request):
    return render(request, "admin_template/html/hos-doctor-profile.html", get_admin_context(request))
def hos_edit_doctor(request):
    return render(request, "admin_template/html/hos-edit-doctor.html", get_admin_context(request))

# modification patient
def hos_edit_patient(request, patient_id):
    context = get_admin_context(request)
    patient = get_object_or_404(Patient, pk=patient_id)
    context['patient'] = patient

    if request.method == "POST":
        nom = request.POST.get("nom")
        prenom = request.POST.get("prenom")
        sexe = request.POST.get("sexe")
        age = request.POST.get("age")
        email = request.POST.get("email")
        numero_carte_identite = request.POST.get("numero_carte_identite")
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")
        photo = request.FILES.get("photo")

        # Vérification unicité email/numéro_carte (hors patient courant)
        if Patient.objects.exclude(pk=patient.pk).filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé par un autre patient.")
            return render(request, "admin_template/html/hos-edit-patient.html", context)
        if Patient.objects.exclude(pk=patient.pk).filter(numero_carte_identite=numero_carte_identite).exists():
            messages.error(request, "Ce numéro de carte d'identité est déjà utilisé par un autre patient.")
            return render(request, "admin_template/html/hos-edit-patient.html", context)
        # Mot de passe : modifié uniquement si rempli et confirmation OK
        if password or password_confirm:
            if password != password_confirm:
                messages.error(request, "Les mots de passe ne correspondent pas.")
                return render(request, "admin_template/html/hos-edit-patient.html", context)
            patient.mot_de_passe = password  # (Pense à hasher en prod !)

        # Met à jour les infos
        patient.nom = nom
        patient.prenom = prenom
        patient.sexe = sexe
        patient.age = age
        patient.email = email
        patient.numero_carte_identite = numero_carte_identite
        if photo:
            patient.photo = photo
        patient.save()
        messages.success(request, "Le patient a bien été modifié.")
        return redirect('hos_all_patients')

    return render(request, "admin_template/html/hos-edit-patient.html", context)

#suppresion patient
def hos_delete_patient(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    if request.method == 'POST':
        patient.delete()
        messages.success(request, "Le patient a bien été supprimé.")
        return redirect('hos_all_patients')
    else:
        # Optionnel : page de confirmation
        return render(request, "admin_template/html/hos-confirm-delete-patient.html", {'patient': patient})

def hos_events(request):
    return render(request, "admin_template/html/hos-events.html", get_admin_context(request))
def hos_faq(request):
    return render(request, "admin_template/html/hos-faq.html", get_admin_context(request))


def hos_patient_dash(request):
    user_id = request.session.get('user_id')
    patient = None
    if user_id:
        try:
            patient = Patient.objects.get(id=user_id)
        except Patient.DoesNotExist:
            patient = None
    return render(request, "admin_template/html/hos-patient-dash.html", {"patient": patient})

def hos_patient_invoice(request):
    return render(request, "admin_template/html/hos-patient-invoice.html", get_admin_context(request))

#profile du patient
def hos_patient_profile(request, id):
    patient = get_object_or_404(Patient, id=id)
    context = {
        'patient': patient,
    }
    return render(request, "admin_template/html/hos-patient-profile.html", context)

def hos_patients(request):
    return render(request, "admin_template/html/hos-patients.html", get_admin_context(request))
def hos_payment(request):
    return render(request, "admin_template/html/hos-payment.html", get_admin_context(request))
def hos_schedule(request):
    return render(request, "admin_template/html/hos-schedule.html", get_admin_context(request))
def hos_staff_profile(request):
    return render(request, "admin_template/html/hos-staff-profile.html", get_admin_context(request))
def hos_support(request):
    return render(request, "admin_template/html/hos-support.html", get_admin_context(request))

# --- INDEX / ACCUEIL ---
def index_dashboard(request):
    return render(request, "admin_template/html/index-dashboard.html", get_admin_context(request))
def index(request):
    return render(request, "admin_template/html/index.html", get_admin_context(request))

# --- UI ---
def ui_404(request):
    return render(request, "admin_template/html/ui-404.html", get_admin_context(request))
def ui_accordion(request):
    return render(request, "admin_template/html/ui-accordion.html", get_admin_context(request))
def ui_alerts(request):
    return render(request, "admin_template/html/ui-alerts.html", get_admin_context(request))
def ui_breadcrumbs(request):
    return render(request, "admin_template/html/ui-breadcrumbs.html", get_admin_context(request))
def ui_buttons(request):
    return render(request, "admin_template/html/ui-buttons.html", get_admin_context(request))
def ui_dropdowns(request):
    return render(request, "admin_template/html/ui-dropdowns.html", get_admin_context(request))
def ui_faq(request):
    return render(request, "admin_template/html/ui-faq.html", get_admin_context(request))
def ui_fontawesome(request):
    return render(request, "admin_template/html/ui-fontawesome.html", get_admin_context(request))
def ui_glyphicons(request):
    return render(request, "admin_template/html/ui-glyphicons.html", get_admin_context(request))
def ui_grids(request):
    return render(request, "admin_template/html/ui-grids.html", get_admin_context(request))
def ui_group_list(request):
    return render(request, "admin_template/html/ui-group-list.html", get_admin_context(request))
def ui_icons(request):
    return render(request, "admin_template/html/ui-icons.html", get_admin_context(request))
def ui_labels_badges(request):
    return render(request, "admin_template/html/ui-labels-badges.html", get_admin_context(request))
def ui_login(request):
    return render(request, "admin_template/html/ui-login.html", get_admin_context(request))
def ui_modals(request):
    return render(request, "admin_template/html/ui-modals.html", get_admin_context(request))
def ui_navbars(request):
    return render(request, "admin_template/html/ui-navbars.html", get_admin_context(request))
def ui_notifications(request):
    return render(request, "admin_template/html/ui-notifications.html", get_admin_context(request))
def ui_pagination(request):
    return render(request, "admin_template/html/ui-pagination.html", get_admin_context(request))
def ui_panels(request):
    return render(request, "admin_template/html/ui-panels.html", get_admin_context(request))
def ui_popovers(request):
    return render(request, "admin_template/html/ui-popovers.html", get_admin_context(request))
def ui_pricing_expanded(request):
    return render(request, "admin_template/html/ui-pricing-expanded.html", get_admin_context(request))
def ui_pricing_narrow(request):
    return render(request, "admin_template/html/ui-pricing-narrow.html", get_admin_context(request))
def ui_progress(request):
    return render(request, "admin_template/html/ui-progress.html", get_admin_context(request))
def ui_register(request):
    return render(request, "admin_template/html/ui-register.html", get_admin_context(request))
def ui_tabs(request):
    return render(request, "admin_template/html/ui-tabs.html", get_admin_context(request))
def ui_timeline_centered(request):
    return render(request, "admin_template/html/ui-timeline-centered.html", get_admin_context(request))
def ui_timeline_left(request):
    return render(request, "admin_template/html/ui-timeline-left.html", get_admin_context(request))
def ui_tooltips(request):
    return render(request, "admin_template/html/ui-tooltips.html", get_admin_context(request))
def ui_typography(request):
    return render(request, "admin_template/html/ui-typography.html", get_admin_context(request))