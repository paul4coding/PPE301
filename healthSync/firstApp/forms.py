from django import forms
from .models import Utilisateur, Specialite,Medecin
from .models import RendezVous, Patient
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
        
    
class MedecinForm(forms.ModelForm):
    class Meta:
        model = Medecin
        fields = [
            'nom',
            'prenom',
            'sexe',
            'age',
            'email',
            'mot_de_passe',
            'photo',
            'specialite'
        ]
        widgets = {
            'mot_de_passe': forms.PasswordInput(render_value=True),
            'sexe': forms.Select(choices=[('M', 'Masculin'), ('F', 'Féminin')]),
        }
        labels = {
            'nom': "Nom",
            'prenom': "Prénom",
            'sexe': "Sexe",
            'age': "Âge",
            'email': "Email",
            'mot_de_passe': "Mot de passe",
            'photo': "Photo",
            'specialite': "Spécialité",
        }

class RendezVousForm(forms.ModelForm):
    class Meta:
        model = RendezVous
        fields = ['medecin', 'patient', 'date', 'heure', 'motif', 'statut']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'heure': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}, format='%H:%M'),
            'motif': forms.TextInput(attrs={'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
            'medecin': forms.Select(attrs={'class': 'form-control'}),
            'patient': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'medecin': "Médecin",
            'patient': "Patient",
            'date': "Date du rendez-vous",
            'heure': "Heure du rendez-vous",
            'motif': "Motif",
            'statut': "Statut",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pour forcer le format de la date dans le champ (important pour la modification !)
        self.fields['date'].input_formats = ['%Y-%m-%d']
        self.fields['heure'].input_formats = ['%H:%M']