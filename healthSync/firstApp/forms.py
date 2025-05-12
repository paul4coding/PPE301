from django import forms
from .models import Utilisateur

class ConnexionForm(forms.Form):
    email = forms.EmailField()
    mot_de_passe = forms.CharField(widget=forms.PasswordInput)

class InscriptionForm(forms.ModelForm):
    mot_de_passe = forms.CharField(widget=forms.PasswordInput)
    user_type = forms.ChoiceField(
        choices=[('patient', 'Patient'), ('personnel', 'Personnel de santé')],
        widget=forms.RadioSelect,
        label="Qui suis-je ?"
    )
    personnel_role = forms.ChoiceField(
        choices=[
            ('medecin', 'Médecin'),
            ('laborantin', 'Laborantin'),
            ('secretaire', 'Secrétaire')
        ],
        required=False,
        label="Quel est votre rôle ?"
    )

    class Meta:
        model = Utilisateur
        fields = ['nom', 'prenom', 'sexe', 'age', 'email', 'mot_de_passe', 'user_type', 'personnel_role']