from django import forms
from .models import Utilisateur, Specialite

class ConnexionForm(forms.Form):
    email = forms.EmailField()
    mot_de_passe = forms.CharField(widget=forms.PasswordInput)

class InscriptionForm(forms.ModelForm):
    mot_de_passe = forms.CharField(widget=forms.PasswordInput)
    photo = forms.ImageField(required=False, label="Photo de profil")
    user_type = forms.ChoiceField(
        choices=[('patient', 'Patient'), ('personnel', 'Personnel de santé')],
        widget=forms.RadioSelect,
        label="Qui suis-je ?"
    )
    personnel_role = forms.ChoiceField(
        choices=[
            ('laborantin', 'Laborantin'),
            ('medecin', 'Médecin'),
            ('secretaire', 'Secrétaire')
        ],
        required=False,
        label="Quel est votre rôle ?"
    )

    specialite = forms.ModelChoiceField(
        queryset=Specialite.objects.all(),
        required=False,
        label="Spécialité (si Médecin)"
    )
    numero_carte_identite = forms.CharField(
        required=False,
        label="Numéro de carte d'identité"
    )

    class Meta:
        model = Utilisateur
        fields = ['nom', 'prenom', 'sexe', 'age', 'email', 'mot_de_passe', 'photo', 'user_type', 'personnel_role','numero_carte_identite']