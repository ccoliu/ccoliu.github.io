//////////////IP SETTINGS/////////////////////
const LOGIN_SERVER = "https://192.168.0.241:56123/";
/////////////////////////////////////////////

const submitButton = document.getElementById("submit-btn");

// 註冊事件
submitButton.addEventListener("click", submit);

// 驗證欄位是否為空
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

// 驗證密碼是否一致
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

// 提交表單
function submit() {
    console.log("Submitting form...");

    // 取得欄位值
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();
    const confirmPassword = document.getElementById("password-conf").value.trim();

    // 驗證欄位
    const isNotEmpty = validateEmpty(username, password);
    const isPasswordValid = validatePassword(password, confirmPassword);

    if (isNotEmpty && isPasswordValid) {
        console.log("Validation passed!");

        // 包裝成 JSON 格式
        const payload = {
            username: username,
            password: password,
        };

        console.log("Payload:", payload);

        // 傳送資料到後端
        fetch(LOGIN_SERVER + "register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    // 成功註冊的提示訊息和操作
                    alert("Registration successful! Redirecting to login page...");
                    window.location.href = "login.html";
                } else {
                    // 根據後端回傳的錯誤訊息，顯示提示
                    alert(`Registration failed: ${data.error}`);
                }
            })
            .catch((error) => {
                // 錯誤處理
                console.error("Error occurred during registration:", error);
                alert("An error occurred while registering. Please try again later.");
            });
    } else {
        console.log("Validation failed!");
    }
}