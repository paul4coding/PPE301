from django.db import models

# Create your models here.


class Utilisateur(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    sexe = models.CharField(max_length=1, choices=[('M', 'Masculin'), ('F', 'Féminin')])
    age = models.IntegerField()
    email = models.EmailField(unique=True)
    mot_de_passe = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.prenom} {self.nom}"
