from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import RendezVous, Notification, Utilisateur

@receiver(post_save, sender=RendezVous)
def notifie_creation_ou_modification_rdv(sender, instance, created, **kwargs):
    patient = instance.patient
    medecin = instance.medecin

    nom_medecin = f"{getattr(medecin, 'nom', '')} {getattr(medecin, 'prenom', '')}".strip()
    nom_patient = f"{getattr(patient, 'nom', '')} {getattr(patient, 'prenom', '')}".strip()
    url = "#"

    Notification.objects.create(
        destinataire=patient,
        message=f"Vous avez un rendez-vous avec le Dr {nom_medecin} le {instance.date} à {instance.heure}.",
        lien=url,
        type="rendezvous"
    )

    Notification.objects.create(
        destinataire=medecin,
        message=f"Vous avez un rendez-vous avec le patient {nom_patient} le {instance.date} à {instance.heure}.",
        lien=url,
        type="rendezvous"
    )

    secretaires = Utilisateur.objects.filter(secretaire=True)  # ← CORRECTION ICI
    for sec in secretaires:
        Notification.objects.create(
            destinataire=sec,
            message=f"Nouveau rendez-vous programmé entre {nom_patient} et Dr {nom_medecin} le {instance.date} à {instance.heure}.",
            lien=url,
            type="rendezvous"
        )

    if not created:
        users = set([patient, medecin]) | set(secretaires)
        for user in users:
            Notification.objects.create(
                destinataire=user,
                message=f"Le statut du rendez-vous du {instance.date} à {instance.heure} a été modifié ({instance.statut}).",
                lien=url,
                type="rendezvous"
            )