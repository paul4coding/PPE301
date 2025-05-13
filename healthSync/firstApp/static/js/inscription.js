document.addEventListener('DOMContentLoaded', function () {
    const userTypeInputs = document.querySelectorAll('input[name="user_type"]');
    const personnelRoleSection = document.getElementById('personnel-role-section');
    const specialiteSection = document.getElementById('specialite-section');
    const personnelRoleInput = document.querySelector('select[name="personnel_role"]');

    // Afficher/Masquer la section "Quel est votre rôle ?" en fonction du type d'utilisateur
    userTypeInputs.forEach(input => {
        input.addEventListener('change', function () {
            if (this.value === 'personnel') {
                personnelRoleSection.style.display = 'block';
            } else {
                personnelRoleSection.style.display = 'none';
                specialiteSection.style.display = 'none';
            }
        });
    });

    // Afficher/Masquer la section "Spécialité" si le rôle sélectionné est "Médecin"
    if (personnelRoleInput) {
        personnelRoleInput.addEventListener('change', function () {
            if (this.value === 'medecin') {
                specialiteSection.style.display = 'block';
            } else {
                specialiteSection.style.display = 'none';
            }
        });
    }
});