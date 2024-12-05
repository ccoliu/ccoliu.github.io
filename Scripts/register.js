
const submitButton = document.getElementById('submit-btn');

submitButton.addEventListener('click', submit);

function validateEmpty() {
    let legal = true;
    const usrname = document.getElementById('username');
    const usrnamwarning = document.querySelector('.username-warning');
    const password = document.getElementById('password');
    const passwordwarning = document.querySelector('.password-warning');
    const confirmPassword = document.getElementById('password-conf');
    const confirmPasswordwarning = document.querySelector('.password-conf-warning');

    if (usrname.value.length == 0) {
        usrname.style.borderColor = 'red';
        usrnamwarning.innerHTML = '*Username cannot be empty.';
        legal = false;  
    }
    else {
        usrname.style.borderColor = 'black';
        usrnamwarning.innerHTML = '';
    }

    if (password.value.length < 6) {
        password.style.borderColor = 'red';
        passwordwarning.innerHTML = '*Password must be at least 6 characters long.';
        legal = false;
    }
    else {
        password.style.borderColor = 'black';
        passwordwarning.innerHTML = '';
    }

    return legal;
}

function validatePassword() {
    const password = document.getElementById('password');
    const passwordwarning = document.querySelector('.password-warning');
    const confirmPassword = document.getElementById('password-conf');
    const confirmPasswordwarning = document.querySelector('.password-conf-warning');

    if (password.value !== confirmPassword.value) {
        password.style.borderColor = 'red';
        confirmPassword.style.borderColor = 'red';
        confirmPasswordwarning.innerHTML = 'Passwords do not match!';
    }
    else {
        password.style.borderColor = 'black';
        confirmPassword.style.borderColor = 'black';
        confirmPasswordwarning.innerHTML = '';
    }
}

function submit() {
    console.log('submitting');
    if (validateEmpty()) validatePassword();
}