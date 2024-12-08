document.addEventListener('DOMContentLoaded', function() {
    const loginbtn = document.getElementById('loginbtn');
    const statusbtn = document.getElementById('statusbtn');
    const logoutbtn = document.getElementById('logoutbtn');
    const warning = document.getElementById('warning');
    const username = document.getElementById('username');
    const password = document.getElementById('password');
    const LOGIN_SERVER = "https://127.0.0.1:56123/";
    let PUBLIC_KEY = ""; // Public key initialized as empty

    // Fetch the public key
    async function fetchPublicKey() {
        try {
            const response = await fetch(`${LOGIN_SERVER}public_key`);
            const data = await response.json();
            if (data.success) {
                PUBLIC_KEY = data.public_key;
                console.log("Fetched Public Key successfully !");
            } else {
                console.error("Failed to fetch public key:", data.error);
            }
        } catch (error) {
            console.error("Failed to fetch public key:", error);
        }
    }

    // Encrypt password
    function encryptPassword(password) {
        const encryptor = new JSEncrypt();
        encryptor.setPublicKey(PUBLIC_KEY);
        return encryptor.encrypt(password);
    }

    // Login button event listener
    loginbtn.addEventListener('click', async function() {
        let legal = true;
        console.log('Login button clicked');
        
        // Validate username and password fields
        if (username.value === '') {
            warning.innerHTML = 'Please enter username/password!';
            username.style.border = '1px solid red';
            legal = false;
        } else {
            username.style.border = '1px solid #ced4da';
        }

        if (password.value === '') {
            warning.innerHTML = 'Please enter username/password!';
            password.style.border = '1px solid red';
            legal = false;
        } else {
            password.style.border = '1px solid #ced4da';
        }

        if (!legal) {
            return;
        }

        // Encrypt the password
        const encryptedPassword = encryptPassword(password.value);
        if (!encryptedPassword) {
            console.error("Password encryption failed!");
            warning.innerHTML = 'Encryption error. Please try again.';
            return;
        }

        // Prepare payload
        const payload = {
            username: username.value.trim(),
            password: encryptedPassword,
        };

        // Send login request to the server
        try {
            const response = await fetch(`${LOGIN_SERVER}login`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload),
            });

            const data = await response.json();

            if (data.success) {
                warning.innerHTML = 'Login successful!';
                warning.style.color = 'green';
                console.log("Login successful");
                
                // Store the token in localStorage for future authenticated requests
                localStorage.setItem('auth_token', data.token);

                // Redirect to a dashboard or other page if needed
                // window.location.href = "/dashboard.html";
            } else {
                warning.innerHTML = 'Invalid username or password.';
                warning.style.color = 'red';
                console.error("Login failed:", data.error);
            }
        } catch (error) {
            console.error("Error during login request:", error);
            warning.innerHTML = 'An error occurred. Please try again later.';
            warning.style.color = 'red';
        }
    });

    // Status button event listener
    statusbtn.addEventListener('click', async function () {
        console.log('Status button clicked');
        try {
            const token = localStorage.getItem('auth_token');
            if (!token) {
                warning.innerHTML = 'No authentication token found.';
                warning.style.color = 'red';
                return;
            }

            const response = await fetch(`${LOGIN_SERVER}verify`, {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${token}`,
                },
            });

            const data = await response.json();

            if (data.success) {
                warning.innerHTML = 'Verification successful!';
                warning.style.color = 'green';
                console.log("Verification successfully !!");
            } else {
                warning.innerHTML = 'Verification failed.';
                warning.style.color = 'red';
                console.error("Verification failed:", data.error);
            }
        } catch (error) {
            console.error("Error during verification request:", error);
            warning.innerHTML = 'An error occurred during verification. Please try again.';
            warning.style.color = 'red';
        }
    });
    
    // Logout button event listener
    logoutbtn.addEventListener('click', async function () {
        console.log('Logout button clicked');
        try {
            const token = localStorage.getItem('auth_token');
            if (!token) {
                warning.innerHTML = 'No authentication token found. Please log in first.';
                warning.style.color = 'red';
                return;
            }

            // Send logout request to the server
            const response = await fetch(`${LOGIN_SERVER}logout`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json",
                },
            });

            const data = await response.json();

            if (data.success) {
                warning.innerHTML = 'Logout successful!';
                warning.style.color = 'green';
                console.log("Logout successfully !!");

                // Clear token from localStorage
                localStorage.removeItem('auth_token');
            } else {
                warning.innerHTML = 'Logout failed.';
                warning.style.color = 'red';
                console.error("Logout failed:", data.error);
            }
        } catch (error) {
            console.error("Error during logout request:", error);
            warning.innerHTML = 'An error occurred during logout. Please try again.';
            warning.style.color = 'red';
        }
    });

    // Fetch the public key on page load
    fetchPublicKey();
});