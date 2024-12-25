document.addEventListener('DOMContentLoaded', async function() {
    //const LOGIN_SERVER = "https://127.0.0.1:56123/";
    //const LOGIN_SERVER = "https://140.118.101.66:56123/";
    const LOGIN_SERVER = "https://140.118.153.31:56123/";
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