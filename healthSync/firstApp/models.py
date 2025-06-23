
from django.db import models
from django.utils import timezone

class Utilisateur(models.Model):
    """Classe parent pour tous les types d'utilisateurs."""
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('medecin', 'Médecin'),
        ('secretaire', 'Secrétaire'),
        ('laborantin', 'Laborantin'),
    ]
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    sexe = models.CharField(max_length=1, choices=[('M', 'Masculin'), ('F', 'Féminin')])
    age = models.IntegerField()
    email = models.EmailField(unique=True)
    mot_de_passe = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='photos/', null=True, blank=True)
    is_validated = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.prenom} {self.nom}"

class Specialite(models.Model):
    """Classe pour les spécialités médicales."""
    nom = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nom

class Patient(Utilisateur):
    """Classe pour les patients."""
    numero_carte_identite = models.CharField(max_length=50, unique=True)

class Laborantin(Utilisateur):
    """Classe pour les laborantins."""


class Medecin(Utilisateur):
    """Classe pour les médecins."""
    specialite = models.ForeignKey(Specialite, on_delete=models.CASCADE)

class Secretaire(Utilisateur):
    """Classe pour les secrétaires."""

class Admin(Utilisateur):
    """Classe pour les administrateurs."""
    pass

class RendezVous(models.Model):
    medecin = models.ForeignKey(Medecin, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()
    heure = models.TimeField()
    motif = models.CharField(max_length=255)
    statut = models.CharField(max_length=20, choices=[
        ('confirmé', 'Confirmé'),
        ('annulé', 'Annulé'),
        ('en_attente', 'En attente')
    ], default='en_attente')
    date_creation = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.patient} avec {self.medecin} le {self.date} à {self.heure}"
    




class DossierPatient(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='dossier')
    liste_allergie = models.TextField(blank=True)
    list_vaccin = models.TextField(blank=True)
    antecedant_medicaux = models.TextField(blank=True)

    def __str__(self):
        return f"Dossier de {self.patient}"

class PageDossierPatient(models.Model):
    dossier = models.ForeignKey(DossierPatient, on_delete=models.CASCADE, related_name='pages')
    date = models.DateField(default=timezone.now)
    temperature = models.FloatField(null=True, blank=True)
    medicaments = models.TextField(blank=True)
    resume_consultation = models.TextField(blank=True, null=True)  

    def __str__(self):
        return f"Page du {self.date} pour {self.dossier.patient}"
    
# --- Notifications ---
class Notification(models.Model):
    destinataire = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    lien = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)
    lu = models.BooleanField(default=False)
    type = models.CharField(max_length=50, default='info')  # 'rendezvous', 'message', etc.

    def __str__(self):
        return f"{self.destinataire} - {self.message[:30]}"

# --- Messagerie ---
class Conversation(models.Model):
    participants = models.ManyToManyField(Utilisateur, related_name='conversations')
    is_group = models.BooleanField(default=False)
    nom_groupe = models.CharField(max_length=100, blank=True, null=True)
    date_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.is_group and self.nom_groupe:
            return self.nom_groupe
        return " & ".join([str(u) for u in self.participants.all()])

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    expediteur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    texte = models.TextField()
    date_envoi = models.DateTimeField(default=timezone.now)
    lu_par = models.ManyToManyField(Utilisateur, related_name='messages_lus', blank=True)

    def __str__(self):
        return f"De {self.expediteur} à {self.date_envoi.strftime('%d/%m/%Y %H:%M')}"


# ...existing code...

class TypeFacture(models.Model):
    intitule = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.intitule

class Service(models.Model):
    type_analyse = models.CharField(max_length=255, blank=True)
    soins = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.type_analyse or self.soins

class Facture(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='factures_patient')
    agent = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True, related_name='factures_agent')
    type_facture = models.ForeignKey(TypeFacture, on_delete=models.SET_NULL, null=True)
    frais = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    services = models.ManyToManyField(Service, through='LigneFacture')

    def __str__(self):
        return f"Facture {self.id} - {self.patient}"

class LigneFacture(models.Model):
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='lignes')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    prix = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.description} ({self.prix} fcfa)"
    
class Resultat(models.Model):
    ligne_facture = models.ForeignKey(LigneFacture, on_delete=models.CASCADE, related_name='resultats')
    resultat = models.TextField()

    def __str__(self):
        return f"Résultat pour {self.ligne_facture}"

class Prescription(models.Model):
    resultat = models.ForeignKey(Resultat, on_delete=models.CASCADE, related_name='prescriptions')
    liste_medicaments = models.TextField()
    posologie = models.TextField()

    def __str__(self):
        return f"Prescription pour {self.resultat}"

