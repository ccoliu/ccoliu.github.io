document.addEventListener('DOMContentLoaded', async function() {
    const LOGIN_SERVER = window.location.origin + "/api/auth/";
    const loginbtn = document.querySelector('.loginUsername');

    const token = localStorage.getItem('auth_token');

    if (token) {
        const response = await fetch(`${LOGIN_SERVER}verify`, {
            method: "GET",
            headers: {
              "Authorization": `Bearer ${token}`,
            },
          })
      
          const data = await response.json();
      
          if (data.success) {
            loginbtn.innerHTML = 'Hello, ' + data.username;
          }
    }
});