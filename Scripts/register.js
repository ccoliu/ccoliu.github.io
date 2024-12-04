
const submitButton = document.getElementById('submit-btn');

submitButton.addEventListener('click', submit);

function validatePassword() {
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('password-conf');
    const warning = document.querySelector('.warning');

    if (password.value !== confirmPassword.value) {
        password.style.borderColor = 'red';
        confirmPassword.style.borderColor = 'red';
        alert('Passwords do not match!');
    }
}

function submit() {
    console.log('submitting');
    validatePassword();
}