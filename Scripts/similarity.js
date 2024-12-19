//////////////IP SETTINGS/////////////////////
const SERVERIP = "https://140.118.101.66:61911/"
//const SERVERIP = "https://127.0.0.1:61911/"
const LOGIN_SERVER = "https://127.0.0.1:56123/";
/////////////////////////////////////////////

const ServerStatus = document.querySelector('.ServerStatus');
const ServerStatusRes = document.querySelector('.ServerStatusRes');

async function fetch_username() {
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        return "Anonymous";
      }
  
      const response = await fetch(`${LOGIN_SERVER}verify`, {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      })
  
      const data = await response.json();
  
      if (data.success) {
        return data.username;
      } else {
        return "Anonymous";
      }
    }
    catch (error) {
      console.error("Error during verification request:", error);
      return "Anonymous";
    }
}

if (ServerStatus && ServerStatusRes) {
    fetch(SERVERIP)
    .then (response => {
        if (!response.ok) {
          ServerStatusRes.innerHTML = "Offline";
          ServerStatusRes.style.color = "red";
        }
        else {
          ServerStatusRes.innerHTML = "Online";
          ServerStatusRes.style.color = "green";
        }
    })
    .catch(error => {
        console.log(error);
        ServerStatusRes.innerHTML = "Blocked/Offline";
        ServerStatusRes.style.color = "red";
    });
}
  
if (ServerStatusRes) {
    ServerStatusRes.addEventListener('click', () => {
        window.open(SERVERIP, '_blank');
    });
}

const sidebar = document.querySelector('.sidebar');
const content = document.querySelector('.content');
const originBodyOverflowY = document.body.style.overflowY;

sidebar.addEventListener('mouseenter', () => {
    // 添加內容區域的暗化效果
    content.classList.add('content-darkened');
    document.body.style.overflowY = 'hidden'; // 鎖定網頁滾動
    if (textOutput) document.getElementById("textOutput").style.overflowY = "hidden";
});

sidebar.addEventListener('mouseleave', () => {
    // 移除內容區域的暗化效果
    content.classList.remove('content-darkened');
    document.body.style.overflowY = originBodyOverflowY; // 解鎖網頁滾動
    if (textOutput && originBodyOverflowY) textOutput.style.overflowY = "auto";
    sidebar.scrollTo({ top: 0, behavior: 'smooth' });
});

function enhanceTextInput(event, element) {
    const keyPairs = {
      Tab: "\t",
      "(": "()",
      "{": "{}",
      "[": "[]",
      '"': '""',
      "'": "''",
      "<": "<>",
    };

    nearestlengthInfo = element.parentElement.querySelector('.lengthInfo');
    console.log(nearestlengthInfo);
  
    if (keyPairs[event.key]) {
      event.preventDefault();
      const { selectionStart, selectionEnd, value } = element;
  
      element.value =
        value.substring(0, selectionStart) +
        keyPairs[event.key] +
        value.substring(selectionEnd);
      element.selectionStart = element.selectionEnd = selectionStart + 1;
    }
    blockLength = element.value.length;
    if (blockLength > 10000) {
      document.querySelector('.footerdesc').style.display = "flex";
      document.querySelector('.footerdesc').style.backgroundColor = "#f66868";
      document.querySelector('.footerdesc').innerHTML = "Can only input 10000 characters!";
      setTimeout(() => {
          document.querySelector('.footerdesc').style.animation = "heightoff 0.75s forwards";
      }, 2000);
      document.querySelector('.footerdesc').style.animation = "heightaddon 0.75s forwards";
      element.value = element.value.substring(0, 10000);
      nearestlengthInfo.innerHTML = "10000/10000 character(s)";
    }
    else {
      nearestlengthInfo.innerHTML = blockLength + "/10000 character(s)";
    }
}

function createErrorMsg(str){
    document.querySelector('.footerdesc').style.display = "flex";
    document.querySelector('.footerdesc').style.backgroundColor = "#f66868";
    document.querySelector('.footerdesc').innerHTML = str;
    setTimeout(() => {
      document.querySelector('.footerdesc').style.animation = "heightoff 0.75s forwards";
    }, 2000);
    document.querySelector('.footerdesc').style.animation = "heightaddon 0.75s forwards";
    return;
}

function createSuccessMsg(str){
    document.querySelector('.footerdesc').style.display = "flex";
    document.querySelector('.footerdesc').style.backgroundColor = "#35f52e";
    document.querySelector('.footerdesc').innerHTML = str;
    setTimeout(() => {
      document.querySelector('.footerdesc').style.animation = "heightoff 0.75s forwards";
    }, 2000);
    document.querySelector('.footerdesc').style.animation = "heightaddon 0.75s forwards";
    return;
}

const textarea = document.querySelector(".textarea");
    textarea.addEventListener("keydown", (event) => {
        if (event.target.matches('textarea')) {
            enhanceTextInput(event, event.target);
        }
    });
    textarea.addEventListener("input", (event) => {
        if (event.target.matches('textarea')) {
            enhanceTextInput(event, event.target);
        }
    });

let uploadButton = document.querySelectorAll(".buttonUpload");
const availableExtensions = ["txt", "py", "js", "html", "css", "c", "cpp", "java","h"];
uploadButton.forEach((button) => {
    button.addEventListener("click", (event) => {
        let target = event.target;
        console.log(target);
        fileInput = target.parentElement.querySelector(".inputfile");
        file = fileInput.files[0];
        if (!file) {
            createErrorMsg("Please select a file.");
            return;
        }

        const filename = file.name;
        const extentions = file.name.split(".");
        const extension = extentions[extentions.length - 1];

        if (!availableExtensions.includes(extension)) {
            createErrorMsg("\"" + filename + "\"" + " is an Invalid file type.");
            return;
        }

        const reader = new FileReader();

        reader.onload = () => {
            event.target.parentElement.parentElement.querySelector('textarea').value = reader.result;
            enhanceTextInput(event, event.target.parentElement.parentElement.querySelector('textarea'));
            fileInput.value = "";
        }

        reader.readAsText(file);
        createSuccessMsg("\"" + filename + "\"" + " has been uploaded successfully.");
    });
    return;
});

const clearbtn = document.querySelector('.buttonClear');
clearbtn.addEventListener("click", () => {
    const textarea = document.querySelectorAll('.textarea textarea');
    textarea.forEach(element => {
        element.value = "";
    })
    return;
})

const submitbtn = document.querySelector('.buttonAnalyse');
submitbtn.addEventListener("click", async () => {

    if (document.querySelector('.input1').value == "") {
        createErrorMsg("Please enter the text.");
        return;
    }

    if (ServerStatusRes.innerHTML == "Must unblock server") {
        document.querySelector('.footerdesc').style.display = "flex";
        document.querySelector('.footerdesc').style.backgroundColor = "#f66868";
        document.querySelector('.footerdesc').innerHTML = "Server is blocked! Click Server Status for more information.";
        setTimeout(() => {
            document.querySelector('.footerdesc').style.animation = "heightoff 0.75s forwards";
        }, 2000);
        document.querySelector('.footerdesc').style.animation = "heightaddon 0.75s forwards";
        return;
    }

    const code1 = document.querySelector('.input1').value;
    const code2 = document.querySelector('.input2').value;
    document.querySelector('.loadinggif').style.display = "flex";

    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });

    const username = await fetch_username();
    console.log(username);
 
    fetch(SERVERIP + "similarity", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({code1, code2, username}),
    })
    .then((response) => response.json())
    .then((data) => {
        console.log(data);
        createSuccessMsg("Similarity analysis has been completed.");
        document.querySelector('.AImsg').style.display = "block";
        document.querySelector('.textOutput').style.display = "block";
        document.querySelector('.textOutput').value = data['result'];
        window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    })
    .catch((error) => {
        console.error("Error:", error);
        createErrorMsg("An error has occurred while processing the code, please try again.");
    })
    .finally(() => {
        document.querySelector('.loadinggif').style.display = "none";
    });
    return;
})
