
from django.db import models

class Utilisateur(models.Model):
    """Classe parent pour tous les types d'utilisateurs."""
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    sexe = models.CharField(max_length=1, choices=[('M', 'Masculin'), ('F', 'Féminin')])
    age = models.IntegerField()
    email = models.EmailField(unique=True)
    mot_de_passe = models.CharField(max_length=100)

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

