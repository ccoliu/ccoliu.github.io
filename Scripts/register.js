// ---------------------------------------------------
// Constants and Global Variables
// ---------------------------------------------------
const LOGIN_SERVER = "https://127.0.0.1:56123/";
let PUBLIC_KEY = ""; // Public key initialized as empty

// ---------------------------------------------------
// Functions
// ---------------------------------------------------

/**
 * Fetch the public key from the server and store it in the PUBLIC_KEY variable.
 */
async function fetchPublicKey() {
    try {
        const response = await fetch(`${LOGIN_SERVER}public_key`);
        const data = await response.json();
        if (data.success) {
            PUBLIC_KEY = data.public_key;
            console.log("Fetched Public Key:", PUBLIC_KEY);
        } else {
            console.error("Failed to fetch public key:", data.error);
        }
    } catch (error) {
        console.error("Failed to fetch public key:", error);
    }
}

/**
 * Encrypt the password using the public key.
 * @param {string} password - The plaintext password to encrypt.
 * @returns {string} The encrypted password.
 */

function encryptPassword(password) {
    const encryptor = new JSEncrypt();
    encryptor.setPublicKey(PUBLIC_KEY);
    return encryptor.encrypt(password);
}

/**
 * Validate if the username and password fields are not empty.
 * @param {string} username - The username input value.
 * @param {string} password - The password input value.
 * @returns {boolean} True if all fields are valid, false otherwise.
 */

function validateEmpty(username, password) {
    let legal = true;
    const usrnamwarning = document.querySelector(".username-warning");
    const passwordwarning = document.querySelector(".password-warning");

    if (username.length === 0) {
        usrnamwarning.innerHTML = "*Username cannot be empty.";
        legal = false;
    } else {
        usrnamwarning.innerHTML = "";
    }

    if (password.length < 6) {
        passwordwarning.innerHTML = "*Password must be at least 6 characters long.";
        legal = false;
    } else {
        passwordwarning.innerHTML = "";
    }

    return legal;
}

/**
 * Validate if the password and confirm password fields match.
 * @param {string} password - The password input value.
 * @param {string} confirmPassword - The confirm password input value.
 * @returns {boolean} True if passwords match, false otherwise.
 */

function validatePassword(password, confirmPassword) {
    const confirmPasswordwarning = document.querySelector(".password-conf-warning");

    if (password !== confirmPassword) {
        confirmPasswordwarning.innerHTML = "Passwords do not match!";
        return false;
    } else {
        confirmPasswordwarning.innerHTML = "";
        return true;
    }
}

/**
 * Handle form submission and registration.
 */

function submit() {
    console.log("Submitting form...");

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();
    const confirmPassword = document.getElementById("password-conf").value.trim();

    const isNotEmpty = validateEmpty(username, password);
    const isPasswordValid = validatePassword(password, confirmPassword);

    if (isNotEmpty && isPasswordValid) {
        // Encrypt the password
        const encryptedPassword = encryptPassword(password);
        console.log("Encrypted Password:", encryptedPassword);

        // Prepare payload
        const payload = {
            username: username,
            password: encryptedPassword,
        };

        // Send the registration request
        fetch(`${LOGIN_SERVER}register`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    alert("Registration successful! Redirecting to login page...");
                    window.location.href = "login.html";
                } else {
                    alert(`Registration failed: ${data.error}`);
                }
            })
            .catch((error) => {
                console.error("Error occurred during registration:", error);
                alert("An error occurred while registering. Please try again later.");
            });
    } else {
        console.log("Validation failed!");
    }
}

// ---------------------------------------------------
// Event Listeners
// ---------------------------------------------------

// Add event listener for the "Submit" button
document.getElementById("submit-btn").addEventListener("click", submit);
// Fetch the public key when the page loads
fetchPublicKey();