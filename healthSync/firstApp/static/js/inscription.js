document.addEventListener('DOMContentLoaded', function () {
    const userTypeInputs = document.querySelectorAll('input[name="user_type"]');
    const personnelRoleSection = document.getElementById('personnel-role-section');

    userTypeInputs.forEach(input => {
        input.addEventListener('change', function () {
            if (this.value === 'personnel') {
                personnelRoleSection.style.display = 'block';
            } else {
                personnelRoleSection.style.display = 'none';
            }
        });
    });
});
