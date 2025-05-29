
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
    