from django.shortcuts import render, redirect, get_object_or_404
from .forms import ConnexionForm, InscriptionForm, MedecinForm
from .models import Utilisateur, Patient, Laborantin, Medecin, Secretaire, Specialite , DossierPatient, PageDossierPatient, Notification, Conversation, Message
from django.views.decorators.http import require_POST
from django.contrib import messages
from .forms import FactureForm, LigneFactureForm, ResultatForm, PrescriptionForm
from .forms import RendezVousForm
from django.db import IntegrityError
from django.utils.timezone import now
from .models import RendezVous,Facture, LigneFacture, Resultat, Prescription, Patient, TypeFacture, Service
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count

# --- WORKFLOW FACTURE ---

@require_POST
def changer_statut_facture(request, facture_id):
    facture = get_object_or_404(Facture, id=facture_id)
    role = get_admin_context(request)['role']
    action = request.POST.get('action')

    if action == 'valider' and role == 'secretaire' and facture.statut == 'brouillon':
        facture.statut = 'validee'
    elif action == 'transfert_secretaire' and role == 'medecin' and facture.statut == 'validee':
        facture.statut = 'attente_secretaire'
    elif action == 'transfert_laborantin' and role == 'secretaire' and facture.statut == 'attente_secretaire':
        facture.statut = 'attente_laborantin'
    elif action == 'transfert_medecin' and role == 'laborantin' and facture.statut == 'attente_laborantin':
        facture.statut = 'attente_medecin'
    elif action == 'cloturer' and role == 'medecin' and facture.statut == 'attente_medecin':
        facture.statut = 'cloturee'
    else:
        # Affiche une page d'accès refusé avec bouton retour accueil
        return render(
            request,
            'admin_template/html/access_forbidden.html',
            {
                'message': "Action non autorisée.",
                'home_url': 'admin_home',  # adapte selon ton url d'accueil
            }
        )

    facture.save()
    return redirect('detail_facture', facture_id=facture.id)

def detail_facture(request, facture_id):
    context = get_admin_context(request)
    facture = get_object_or_404(Facture, id=facture_id)
    user = context['user']
    role = context['role']

    # Contrôle d'accès selon le statut de la facture
    if facture.statut == 'brouillon' and role != 'secretaire':
        return HttpResponseForbidden("Facture non validée par le secrétaire.")
    if facture.statut == 'validee' and role != 'medecin':
        return HttpResponseForbidden("Facture en attente de validation par le médecin.")
    if facture.statut == 'attente_secretaire' and role != 'secretaire':
        return HttpResponseForbidden("Facture en attente de traitement par le secrétaire.")
    if facture.statut == 'attente_laborantin' and role != 'laborantin':
        return HttpResponseForbidden("Facture en attente de traitement par le laborantin.")
    if facture.statut == 'attente_medecin' and role != 'medecin':
        return HttpResponseForbidden("Facture en attente de traitement par le médecin.")
    if facture.statut == 'cloturee' and role not in ['medecin', 'patient']:
        return HttpResponseForbidden("Facture clôturée.")

    lignes = facture.lignes.all()
    total = sum(ligne.prix for ligne in lignes)
    context['facture'] = facture
    context['lignes'] = lignes
    context['total'] = total
    return render(request, 'admin_template/html/facture_detail.html', context)

def creer_facture(request):
    context = get_admin_context(request)
    context['patients'] = Patient.objects.filter(dossier__isnull=False).distinct()
    if request.method == 'POST':
        form = FactureForm(request.POST)
        patient_id = request.POST.get('patient')
        if form.is_valid() and patient_id:
            patient = get_object_or_404(Patient, id=patient_id)
            facture = form.save(commit=False)
            facture.patient = patient
            facture.statut = 'brouillon'
            user_id = request.session.get('user_id')
            if user_id:
                from .models import Utilisateur
                facture.agent = Utilisateur.objects.get(id=user_id)
            else:
                facture.agent = None
            facture.save()
            return redirect('detail_facture', facture_id=facture.id)
    else:
        form = FactureForm()
    context['form'] = form
    return render(request, 'admin_template/html/facture_create_select_patient.html', context)

def ajouter_ligne_facture(request, facture_id):
    context = get_admin_context(request)
    facture = get_object_or_404(Facture, id=facture_id)
    role = context['role']
    # Secrétaire peut ajouter en brouillon, médecin peut ajouter en 'validee' ou 'attente_medecin'
    if not (
        (role == 'secretaire' and facture.statut == 'brouillon') or
        (role == 'medecin' and facture.statut in ['validee', 'attente_medecin'])
    ):
        return HttpResponseForbidden("Vous ne pouvez pas ajouter de ligne à cette étape.")

    context['facture'] = facture
    if request.method == 'POST':
        form = LigneFactureForm(request.POST)
        if form.is_valid():
            ligne = form.save(commit=False)
            ligne.facture = facture
            ligne.save()
            return redirect('detail_facture', facture_id=facture.id)
    else:
        form = LigneFactureForm()
    context['form'] = form
    return render(request, 'admin_template/html/ligne_facture_form.html', context)

# --- FIN WORKFLOW FACTURE ---

def bilan_patient(request):
    context = get_admin_context(request)
    user = context.get('user')
    try:
        patient = user.patient
    except AttributeError:
        context['error'] = "Accès réservé aux patients."
        return render(request, 'admin_template/html/bilan_patient.html', context)
    resultats = Resultat.objects.filter(ligne_facture__facture__patient=patient)
    prescriptions = Prescription.objects.filter(resultat__ligne_facture__facture__patient=patient)
    context['resultats'] = resultats
    context['prescriptions'] = prescriptions
    context['patient'] = patient
    return render(request, 'admin_template/html/bilan_patient.html', context)

def delete_resultat(request, resultat_id):
    context = get_admin_context(request)
    resultat = get_object_or_404(Resultat, id=resultat_id)
    ligne = getattr(resultat, 'ligne_facture', None)
    facture = getattr(ligne, 'facture', None) if ligne else None
    facture_id = getattr(facture, 'id', None)
    if request.method == 'POST':
        resultat.delete()
        messages.success(request, "Résultat supprimé avec succès.")
        if facture_id:
            return redirect('detail_facture', facture_id=facture_id)
        else:
            messages.error(request, "Impossible de retrouver la facture liée à ce résultat.")
            return redirect('liste_factures')
    context['resultat'] = resultat
    return render(request, 'admin_template/html/confirm_delete_resultat.html', context)

def edit_resultat(request, resultat_id):
    context = get_admin_context(request)
    resultat = get_object_or_404(Resultat, id=resultat_id)
    user = context['user']
    role = context['role']
    if role != 'laborantin':
        return HttpResponseForbidden("Seul le laborantin peut modifier le résultat.")
    if request.method == 'POST':
        form = ResultatForm(request.POST, instance=resultat)
        if form.is_valid():
            form.save()
            messages.success(request, "Résultat modifié avec succès.")
            ligne = getattr(resultat, 'ligne_facture', None)
            facture = getattr(ligne, 'facture', None) if ligne else None
            facture_id = getattr(facture, 'id', None)
            if facture_id:
                return redirect('detail_facture', facture_id=facture_id)
            else:
                messages.error(request, "Impossible de retrouver la facture liée à ce résultat.")
                return redirect('liste_factures')
    else:
        form = ResultatForm(instance=resultat)
    context['form'] = form
    context['resultat'] = resultat
    return render(request, 'admin_template/html/resultat_form.html', context)

def edit_facture(request, facture_id):
    context = get_admin_context(request)
    facture = get_object_or_404(Facture, id=facture_id)
    if request.method == 'POST':
        form = FactureForm(request.POST, instance=facture)
        if form.is_valid():
            form.save()
            messages.success(request, "Facture modifiée avec succès.")
            return redirect('detail_facture', facture_id=facture.id)
    else:
        form = FactureForm(instance=facture)
    context['form'] = form
    context['facture'] = facture
    return render(request, 'admin_template/html/facture_edit.html', context)

def delete_facture(request, facture_id):
    context = get_admin_context(request)
    facture = get_object_or_404(Facture, id=facture_id)
    if request.method == 'POST':
        facture.delete()
        messages.success(request, "Facture supprimée avec succès.")
        return redirect('liste_factures')
    context['facture'] = facture
    return render(request, 'admin_template/html/facture_confirm_delete.html', context)

def edit_prescription(request, prescription_id):
    context = get_admin_context(request)
    prescription = get_object_or_404(Prescription, id=prescription_id)
    user = context['user']
    role = context['role']
    if role != 'medecin':
        return HttpResponseForbidden("Seul le médecin peut modifier la prescription.")
    if request.method == 'POST':
        form = PrescriptionForm(request.POST, instance=prescription)
        if form.is_valid():
            form.save()
            messages.success(request, "Prescription modifiée avec succès.")
            resultat = getattr(prescription, 'resultat', None)
            ligne = getattr(resultat, 'ligne_facture', None) if resultat else None
            facture = getattr(ligne, 'facture', None) if ligne else None
            facture_id = getattr(facture, 'id', None)
            if facture_id:
                return redirect('detail_facture', facture_id=facture_id)
            else:
                return redirect('liste_factures')
    else:
        form = PrescriptionForm(instance=prescription)
    context['form'] = form
    context['prescription'] = prescription
    return render(request, 'admin_template/html/prescription_form.html', context)

def delete_prescription(request, prescription_id):
    context = get_admin_context(request)
    prescription = get_object_or_404(Prescription, id=prescription_id)
    user = context['user']
    role = context['role']
    # Seul le médecin peut supprimer une prescription
    if role != 'medecin':
        return HttpResponseForbidden("Seul le médecin peut supprimer la prescription.")
    resultat = prescription.resultat
    facture_id = resultat.ligne_facture.facture.id if resultat and resultat.ligne_facture and resultat.ligne_facture.facture else None
    if request.method == 'POST':
        prescription.delete()
        messages.success(request, "Prescription supprimée avec succès.")
        if facture_id:
            return redirect('detail_facture', facture_id=facture_id)
        else:
            return redirect('liste_factures')
    context['prescription'] = prescription
    return render(request, 'admin_template/html/confirm_delete_prescription.html', context)

def liste_factures(request):
    context = get_admin_context(request)
    user = context['user']
    role = context['role']
    if role == 'patient':
        factures = Facture.objects.filter(patient=user)
    elif role in ['medecin', 'secretaire', 'laborantin']:
        factures = Facture.objects.all()
    else:
        factures = []
    context['factures'] = factures
    context['total_general'] = sum(f.frais for f in factures)
    return render(request, 'admin_template/html/facture_list.html', context)

def ajouter_resultat(request, ligne_id):
    context = get_admin_context(request)
    ligne = get_object_or_404(LigneFacture, id=ligne_id)
    context['ligne'] = ligne
    user = context['user']
    role = context['role']
    is_patient_concerne = (
        role == 'patient' and ligne.facture.patient == user
    )
    if not (role == 'laborantin' or role == 'medecin' or is_patient_concerne):
        return HttpResponseForbidden("Accès refusé.")
    if request.method == 'POST':
        if role != 'laborantin':
            return HttpResponseForbidden("Seul le laborantin peut modifier le résultat.")
        form = ResultatForm(request.POST)
        if form.is_valid():
            resultat = form.save(commit=False)
            resultat.ligne_facture = ligne
            resultat.save()
            return redirect('detail_facture', facture_id=ligne.facture.id)
    else:
        resultat = getattr(ligne, 'resultat', None)
        form = ResultatForm(instance=resultat) if role == 'laborantin' else None
        context['resultat'] = resultat
    context['form'] = form if role == 'laborantin' else None
    return render(request, 'admin_template/html/resultat_form.html', context)

def ajouter_prescription(request, resultat_id):
    context = get_admin_context(request)
    resultat = get_object_or_404(Resultat, id=resultat_id)
    context['resultat'] = resultat
    user = context['user']
    role = context['role']
    is_patient_concerne = (
        role == 'patient' and resultat.ligne_facture.facture.patient == user
    )
    if not (role == 'medecin' or is_patient_concerne):
        return HttpResponseForbidden("Accès refusé.")
    if request.method == 'POST':
        if role != 'medecin':
            return HttpResponseForbidden("Seul le médecin peut modifier la prescription.")
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.resultat = resultat
            prescription.save()
            return redirect('detail_facture', facture_id=resultat.ligne_facture.facture.id)
    else:
        prescription = getattr(resultat, 'prescription', None)
        form = PrescriptionForm(instance=prescription) if role == 'medecin' else None
        context['prescription'] = prescription
    context['form'] = form if role == 'medecin' else None
    return render(request, 'admin_template/html/prescription_form.html', context)






# Liste des dossiers patients (accessible secrétaire et médecin)
def liste_dossiers_patients(request):
    context = get_admin_context(request)
    context['dossiers'] = DossierPatient.objects.select_related('patient').all()
    return render(request, 'admin_template/html/liste_dossiers_patients.html', context)

# Création d'un dossier patient (secrétaire uniquement)
def creer_dossier_patient(request):
    context = get_admin_context(request)
    context['patients'] = Patient.objects.filter(dossier__isnull=True)
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        patient = get_object_or_404(Patient, id=patient_id)
        DossierPatient.objects.create(patient=patient)
        messages.success(request, "Dossier créé avec succès.")
        return redirect('liste_dossiers_patients')
    return render(request, 'admin_template/html/creer_dossier_patient.html', context)

# Modifier un dossier patient (allergies, vaccins, antécédents)
def edit_dossier_patient(request, dossier_id):
    context = get_admin_context(request)
    dossier = get_object_or_404(DossierPatient, id=dossier_id)
    context['dossier'] = dossier
    if request.method == 'POST':
        dossier.liste_allergie = request.POST.get('liste_allergie', '')
        dossier.list_vaccin = request.POST.get('list_vaccin', '')
        dossier.antecedant_medicaux = request.POST.get('antecedant_medicaux', '')
        dossier.save()
        messages.success(request, "Dossier modifié avec succès.")
        return redirect('hos_patient_profile', patient_id=dossier.patient.id)
    return render(request, 'admin_template/html/edit_dossier_patient.html', context)

def delete_dossier_patient(request, dossier_id):
    context = get_admin_context(request)
    dossier = get_object_or_404(DossierPatient, id=dossier_id)
    context['dossier'] = dossier
    if request.method == 'POST':
        dossier.delete()
        messages.success(request, "Le dossier patient a bien été supprimé.")
        return redirect('liste_dossiers_patients')
    return render(request, 'admin_template/html/confirm_delete_dossier.html', context)

# Ajouter une page (jour) au dossier patient
def add_page_dossier_patient(request, dossier_id):
    context = get_admin_context(request)
    dossier = get_object_or_404(DossierPatient, id=dossier_id)
    context['dossier'] = dossier
    if request.method == 'POST':
        temperature = request.POST.get('temperature')
        medicaments = request.POST.get('medicaments', '')
        PageDossierPatient.objects.create(
            dossier=dossier,
            temperature=temperature,
            medicaments=medicaments
        )
        messages.success(request, "Nouvelle page ajoutée.")
        return redirect('hos_patient_profile', patient_id=dossier.patient.id)
    return render(request, 'admin_template/html/add_page_dossier_patient.html', context)

# Modifier une page (jour) du dossier patient
def edit_page_dossier_patient(request, page_id):
    context = get_admin_context(request)
    page = get_object_or_404(PageDossierPatient, id=page_id)
    context['page'] = page
    role = context.get('role')
    if request.method == 'POST':
        if role == 'secretaire':
            page.temperature = request.POST.get('temperature')
        elif role == 'medecin':
            page.medicaments = request.POST.get('medicaments', '')
            page.resume_consultation = request.POST.get('resume_consultation', '')
        page.save()
        messages.success(request, "Page modifiée avec succès.")
        return redirect('hos_patient_profile', patient_id=page.dossier.patient.id)
    return render(request, 'admin_template/html/edit_page_dossier_patient.html', context)

# Affichage du profil/dossier patient
def hos_patient_profile(request, patient_id):
    context = get_admin_context(request)
    patient = get_object_or_404(Patient, id=patient_id)
    dossier = getattr(patient, 'dossier', None)
    context.update({
        'patient': patient,
        'dossier': dossier,
        'can_edit_dossier': context['role'] in ['secretaire', 'medecin'],
        'can_add_page': context['role'] in ['secretaire', 'medecin'],
        'can_edit_page': context['role'] in ['secretaire', 'medecin'],
    })
    return render(request, 'admin_template/html/hos-patient-profile.html', context)

# modifier rendez vous 
def modifier_rendezvous(request, rdv_id):
    context = get_admin_context(request)
    rdv = get_object_or_404(RendezVous, id=rdv_id)
    context['rdv'] = rdv

    if request.method == "POST":
        form = RendezVousForm(request.POST, instance=rdv)
        context['form'] = form
        if form.is_valid():
            form.save()
            messages.success(request, "Le rendez-vous a bien été modifié !")
            return redirect('liste_rendezvous')
        else:
            messages.error(request, "Merci de corriger les erreurs dans le formulaire.")
    else:
        form = RendezVousForm(instance=rdv)
        context['form'] = form

    return render(request, "admin_template/html/modifier_rendezvous.html", context)


#supprimer rendez vous
def supprimer_rendezvous(request, rdv_id):
    if request.method == "POST":
        rdv = get_object_or_404(RendezVous, id=rdv_id)
        rdv.delete()
        messages.success(request, "Le rendez-vous a été supprimé avec succès !")
    return redirect('liste_rendezvous')

# Liste des rendez vous 
def liste_rendezvous(request):
    # Ajoute les variables user et role dans le contexte grâce à get_admin_context
    context = get_admin_context(request)
    # Récupère tous les rendez-vous, patients et médecins liés (optimisation)
    rdvs = RendezVous.objects.select_related('patient', 'medecin').all().order_by('date', 'heure')
    context['rendezvous'] = rdvs

    # Optionnel : gestion d'un message popup depuis l'URL
    popup_message = request.GET.get("popup_message")
    if popup_message:
        context["popup_message"] = popup_message

    return render(request, "admin_template/html/liste_rendezvous.html", context)

def hos_events(request):
    if not request.user.is_authenticated:
        return redirect('login')

    context = get_admin_context(request)
    user = context.get('user')

    if user is None:
        return redirect('login')

    if hasattr(user, 'medecin'):
        rendezvous = RendezVous.objects.filter(medecin=user.medecin)
    elif hasattr(user, 'patient'):
        rendezvous = RendezVous.objects.filter(patient=user.patient)
    else:
        rendezvous = RendezVous.objects.all()

    # Détection des rendez-vous du jour
    today = now().date()
    has_today = rendezvous.filter(date=today).exists()

    context.update({
        'rendezvous': rendezvous,
        'popup_message': "Vous avez un rendez-vous aujourd’hui !" if has_today else "",
    })

    return render(request, "admin_template/html/hos-schedule.html", context)

def ajouter_rendezvous(request):
    if request.method == "POST":
        patient_id = request.POST.get("patient")
        medecin_id = request.POST.get("medecin")
        date = request.POST.get("date")
        heure = request.POST.get("heure")
        motif = request.POST.get("motif")

        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            messages.error(request, "Patient non trouvé.")
            return redirect('ajouter_rendezvous')

        try:
            medecin = Medecin.objects.get(id=medecin_id)
        except Medecin.DoesNotExist:
            messages.error(request, "Médecin non trouvé.")
            return redirect('ajouter_rendezvous')

        rdv = RendezVous.objects.create(
            patient=patient,
            medecin=medecin,
            date=date,
            heure=heure,
            motif=motif,
        )
        # --- NOTIFICATIONS ---
        Notification.objects.create(
            destinataire=medecin,
            message=f"Un nouveau rendez-vous a été planifié avec le patient {patient.prenom} {patient.nom} le {date} à {heure}.",
            type="rendezvous"
        )
        Notification.objects.create(
            destinataire=patient,
            message=f"Votre rendez-vous avec le Dr {medecin.prenom} {medecin.nom} a été planifié pour le {date} à {heure}.",
            type="rendezvous"
        )
        messages.success(request, "Rendez-vous ajouté avec succès.")
        return redirect('liste_rendezvous')

    # Pour la méthode GET, il faut envoyer la liste des patients et médecins pour le formulaire
    patients = Patient.objects.all()
    medecins = Medecin.objects.all()
    context = {
        'patients': patients,
        'medecins': medecins,
    }
    return render(request, 'admin_template/html/ajouter_rendezvous.html', context)





def api_rendezvous(request):
    rdvs = RendezVous.objects.select_related('patient', 'medecin').all()
    data = []
    for rdv in rdvs:
        event = {
            "id": rdv.id,
            "title": f"{rdv.patient.nom} avec {rdv.medecin.nom} - {rdv.motif}",
            "start": f"{rdv.date}T{str(rdv.heure)[:5]}",
            "color": (
                "#28a745" if rdv.statut == "confirmé" else
                "#dc3545" if rdv.statut == "annulé" else
                "#007bff" if rdv.statut == "recu" else
                "#ffc107"
            ),
            "extendedProps": {
                "patient": rdv.patient.nom,
                "patient_tel": getattr(rdv.patient, "telephone", ""),
                "medecin": rdv.medecin.nom,
                "motif": rdv.motif,
                "statut": rdv.get_statut_display(),
                "date": str(rdv.date),
                "heure": str(rdv.heure)[:5],
            }
        }
        data.append(event)
    return JsonResponse(data, safe=False)

# bouton mettre a jour statut rendez vous dzns tableau 
def set_rdv_status(request):
    if request.method == "POST":
        rdv_id = request.POST.get("rdv_id")
        statut = request.POST.get("statut")
        rdv = get_object_or_404(RendezVous, id=rdv_id)
        rdv.statut = statut
        rdv.save()  # Le signal post_save va gérer les notifications !
        messages.success(request, "Statut du rendez-vous modifié !")
        return redirect('hos_schedule')
    return redirect('hos_schedule')

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
    nb_messages_non_lus = 0
    if user_id:
        try:
            user = Utilisateur.objects.get(id=user_id)
            role = get_user_role(user)
            # Calcul du nombre de messages non lus
            from .models import Message
            nb_messages_non_lus = Message.objects.filter(
                conversation__participants=user
            ).exclude(lu_par=user).count()
        except Utilisateur.DoesNotExist:
            user = None
            role = None
    return {
        'user': user,
        'role': role,
        'roles_pages_acces': ROLES_PAGES_ACCES,
        'roles_support': ROLES_SUPPORT,
        'nb_messages_non_lus': nb_messages_non_lus,  # <--- AJOUT ICI
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

#ajout de medecin
def hos_add_doctor(request):
    context = get_admin_context(request)
    context['specialites'] = Specialite.objects.all()

    if request.method == "POST":
        nom = request.POST.get("nom")
        prenom = request.POST.get("prenom")
        sexe = request.POST.get("sexe")
        age = request.POST.get("age")
        email = request.POST.get("email")
        mot_de_passe = request.POST.get("mot_de_passe")
        mot_de_passe_confirm = request.POST.get("mot_de_passe_confirm")
        specialite_id = request.POST.get("specialite")
        photo = request.FILES.get("photo")

        # Vérification du mot de passe
        if mot_de_passe != mot_de_passe_confirm:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return render(request, "admin_template/html/hos-add-doctor.html", context)

        # Vérification email unique
        if Medecin.objects.filter(email=email).exists():
            messages.error(request, "Cet email existe déjà.")
            return render(request, "admin_template/html/hos-add-doctor.html", context)

        # Récupérer la spécialité
        try:
            specialite = Specialite.objects.get(pk=specialite_id)
        except Specialite.DoesNotExist:
            messages.error(request, "Spécialité invalide.")
            return render(request, "admin_template/html/hos-add-doctor.html", context)

        # Création du médecin
        medecin = Medecin(
            nom=nom,
            prenom=prenom,
            sexe=sexe,
            age=age,
            email=email,
            mot_de_passe=mot_de_passe,  # Hash si tu veux, sinon plaintext, mais déconseillé en prod
            specialite=specialite,
            photo=photo
        )
        medecin.save()
        messages.success(request, "Médecin ajouté avec succès.")
        return redirect('hos_all_doctors')

    return render(request, "admin_template/html/hos-add-doctor.html", context)

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

#affichage tous les docteurs 
def hos_all_doctors(request):
    context = get_admin_context(request)
    context['medecins'] = Medecin.objects.select_related('specialite').all()
    return render(request, "admin_template/html/hos-all-doctors.html", context)


def hos_all_patients(request):
    context = get_admin_context(request)
    context['patients'] = Patient.objects.all()
    return render(request, "admin_template/html/hos-all-patients.html", context)


#Ajout rendez-vous
def hos_book_appointment(request):
    context = get_admin_context(request)
    if request.method == "POST":
        form = RendezVousForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Rendez-vous enregistré avec succès !")
            return redirect('hos_book_appointment')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = RendezVousForm()
    context["form"] = form
    return render(request, "admin_template/html/hos-book-appointment.html", context)




def hos_doctor_dash(request):
    return render(request, 'admin_template/html/hos-patient-dash.html', {'patient': patient})


def hos_doctor_profile(request):
    return render(request, "admin_template/html/hos-doctor-profile.html", get_admin_context(request))

# Vue pour modifier un médecin
def hos_edit_doctor(request, medecin_id):
    context = get_admin_context(request)
    medecin = get_object_or_404(Medecin, pk=medecin_id)
    context['medecin'] = medecin
    context['specialites'] = Specialite.objects.all()

    if request.method == "POST":
        nom = request.POST.get("nom")
        prenom = request.POST.get("prenom")
        sexe = request.POST.get("sexe")
        age = request.POST.get("age")
        email = request.POST.get("email")
        specialite_id = request.POST.get("specialite")
        password = request.POST.get("mot_de_passe")
        password_confirm = request.POST.get("mot_de_passe_confirm")
        photo = request.FILES.get("photo")

        # Vérification unicité email (hors médecin courant)
        if Medecin.objects.exclude(pk=medecin.pk).filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé par un autre médecin.")
            return render(request, "admin_template/html/hos-edit-doctor.html", context)
        # Vérification de la spécialité
        try:
            specialite = Specialite.objects.get(pk=specialite_id)
        except Specialite.DoesNotExist:
            messages.error(request, "Spécialité invalide.")
            return render(request, "admin_template/html/hos-edit-doctor.html", context)
        # Mot de passe : modifié uniquement si rempli et confirmation OK
        if password or password_confirm:
            if password != password_confirm:
                messages.error(request, "Les mots de passe ne correspondent pas.")
                return render(request, "admin_template/html/hos-edit-doctor.html", context)
            medecin.mot_de_passe = password  # (Hash en prod !)

        # Met à jour les infos
        medecin.nom = nom
        medecin.prenom = prenom
        medecin.sexe = sexe
        medecin.age = age
        medecin.email = email
        medecin.specialite = specialite
        if photo:
            medecin.photo = photo
        medecin.save()
        messages.success(request, "Le médecin a bien été modifié.")
        return redirect('hos_all_doctors')

    return render(request, "admin_template/html/hos-edit-doctor.html", context)


# Vue pour supprimer un médecin
def hos_delete_doctor(request, medecin_id):
    medecin = get_object_or_404(Medecin, pk=medecin_id)
    context = get_admin_context(request)  # Ajout du contexte global
    context['medecin'] = medecin
    if request.method == "POST":
        medecin.delete()
        messages.success(request, "Le médecin a été supprimé avec succès.")
        return redirect('hos_all_doctors')
    # Optionnel : page de confirmation
    return render(request, 'admin_template/html/hos-confirm-delete-doctor.html', context)

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

def hos_faq(request):
    return render(request, "admin_template/html/hos-faq.html", get_admin_context(request))

# vue pour le dahboard du patient  ane pas confondre avec celui des medecins 
def hos_patient_dash(request):
    user_id = request.session.get('user_id')
    patient = None
    dossier = None
    if user_id:
        try:
            patient = Patient.objects.get(id=user_id)
            dossier = getattr(patient, 'dossier', None)
        except Patient.DoesNotExist:
            patient = None
            dossier = None
    context = {
        "patient": patient,
        "dossier": dossier,
        "role": "patient",
    }
    return render(request, "admin_template/html/hos-patient-dash.html", context)

def hos_patient_invoice(request):
    return render(request, "admin_template/html/hos-patient-invoice.html", get_admin_context(request))


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

def all_notifications(request):
    context = get_admin_context(request)
    notifications = Notification.objects.all().order_by('-date')
    context['notifications'] = notifications
    return render(request, "admin_template/html/all_notifications.html", context)


def messagerie_inbox(request):
    context = get_admin_context(request)
    user = context['user']

    conversations = Conversation.objects.filter(participants=user).annotate(
        nb_non_lus=Count('messages', filter=~Q(messages__lu_par=user))
    ).distinct().order_by('-messages__date_envoi')
    context['conversations'] = conversations
    return render(request, 'admin_template/html/messagerie_inbox.html', context)

def messagerie_conversation(request, conversation_id):
    context = get_admin_context(request)
    user = context['user']
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=user)
    autres_participants = conversation.participants.exclude(id=user.id)

    # Marquer tous les messages reçus comme lus pour l'utilisateur courant
    messages_a_lire = conversation.messages.exclude(expediteur=user).exclude(lu_par=user)
    for m in messages_a_lire:
        m.lu_par.add(user)

    # Envoi du message
    if request.method == "POST":
        texte = request.POST.get("texte", "").strip()
        if texte:
            m = Message.objects.create(
                conversation=conversation,
                expediteur=user,
                texte=texte
            )
            m.lu_par.add(user)
            m.save()
            return redirect('messagerie_conversation', conversation_id=conversation.id)

    context['conversation'] = conversation
    context['autres_participants'] = autres_participants
    context['messages'] = conversation.messages.order_by('date_envoi')
    return render(request, 'admin_template/html/messagerie_conversation.html', context)

def messagerie_nouvelle_conversation(request):
    context = get_admin_context(request)
    context['medecins'] = Medecin.objects.all()
    context['laborantins'] = Laborantin.objects.all()
    context['secretaires'] = Secretaire.objects.all()
    context['patients'] = Patient.objects.all()

    if request.method == "POST":
        for champ, model in [
            ('destinataire_medecin', Medecin),
            ('destinataire_laborantin', Laborantin),
            ('destinataire_secretaire', Secretaire),
            ('destinataire_patient', Patient),
        ]:
            destinataire_id = request.POST.get(champ)
            if destinataire_id:
                destinataire = model.objects.get(id=destinataire_id)
                conv = Conversation.objects.filter(participants=context['user']).filter(participants=destinataire).distinct()
                if conv.exists():
                    conversation = conv.first()
                else:
                    conversation = Conversation.objects.create()
                    conversation.participants.add(context['user'], destinataire)
                return redirect('messagerie_conversation', conversation_id=conversation.id)
    return render(request, 'admin_template/html/messagerie_nouvelle_conversation.html', context)

def api_recherche_utilisateurs(request):
    role = request.GET.get('role')
    q = request.GET.get('q', '').strip()
    user = get_admin_context(request)['user']
    users = Utilisateur.objects.exclude(id=user.id)
    # Correction ici : filtrer selon le champ booléen correspondant
    if role:
        if role in ['medecin', 'laborantin', 'secretaire', 'patient']:
            users = users.filter(**{role: True})
    if q:
        users = users.filter(
            Q(prenom__icontains=q) |
            Q(nom__icontains=q) |
            Q(email__icontains=q)
        )
    data = [
        {
            "id": u.id,
            "nom": u.nom,
            "prenom": u.prenom,
            "email": u.email,
        }
        for u in users[:10]
    ]
    return JsonResponse({"results": data})

def get_or_create_conversation(user1, user2):
    conversation = (
        Conversation.objects
        .annotate(pcount=Count('participants'))
        .filter(participants=user1)
        .filter(participants=user2)
        .filter(pcount=2)
        .first()
    )
    if conversation:
        return conversation
    conversation = Conversation.objects.create()
    conversation.participants.add(user1, user2)
    return conversation

def messagerie_commencer_conversation(request, user_id):
    current_user = get_admin_context(request)['user']
    destinataire = get_object_or_404(Utilisateur, id=user_id)
    if destinataire.id == current_user.id:
        return redirect('messagerie_inbox')
    conversation = get_or_create_conversation(current_user, destinataire)
    return redirect('messagerie_conversation', conversation_id=conversation.id)

# API pour le chat temps réel
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

def api_get_messages(request, conversation_id):
    user = get_admin_context(request)['user']
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=user)
    messages_objs = conversation.messages.order_by('date_envoi')
    data = []
    for m in messages_objs:
        data.append({
            "id": m.id,
            "auteur": f"{m.auteur.prenom} {m.auteur.nom}",
            "texte": m.texte,
            "date": m.date_envoi.strftime("%d/%m/%Y %H:%M"),
            "is_me": m.auteur == user,
        })
    # Marquer messages comme lus
    conversation.messages.exclude(lu_par=user).filter(~Q(auteur=user)).update(lu_par=user)
    return JsonResponse({"messages": data})

@csrf_exempt
def api_send_message(request, conversation_id):
    if request.method == "POST":
        user = get_admin_context(request)['user']
        conversation = get_object_or_404(Conversation, id=conversation_id, participants=user)
        texte = request.POST.get("texte", "").strip()
        if texte:
            m = Message.objects.create(
                conversation=conversation,
                auteur=user,
                texte=texte,
                date_envoi=timezone.now()
            )
            m.lu_par.add(user)
            m.save()
            return JsonResponse({"success": True})
    return JsonResponse({"success": False})


def marquer_tout_comme_lu(request):
    if request.method == "POST":
        request.session['notifications_marquees_lues'] = True
        return JsonResponse({"success": True})
    return JsonResponse({"error": "Requête invalide"}, status=400)