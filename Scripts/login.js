document.addEventListener('DOMContentLoaded', function() {
    const loginbtn = document.getElementById('loginbtn');
    const warning = document.getElementById('warning');
    const username = document.getElementById('username');
    const password = document.getElementById('password');

    loginbtn.addEventListener('click', function() {
        let legal = true;
        console.log('login button clicked');
        
        if (username.value === '') {
            warning.innerHTML = 'Please enter username/password!';
            username.style.border = '1px solid red';
            legal = false;
        }
        else {
            username.style.border = '1px solid #ced4da';
        }

        if (password.value === '') {
            warning.innerHTML = 'Please enter username/password!';
            password.style.border = '1px solid red';
            legal = false;
        }
        else {
            password.style.border = '1px solid #ced4da';
        }

        if (!legal) {
            return;
        }

        warning.innerHTML = '';
        username.style.border = '1px solid #ced4da';
        password.style.border = '1px solid #ced4da';

    });
});