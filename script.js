// Helper function to toggle the visibility of elements
function toggleVisibility(elementId, display) {
  const element = document.getElementById(elementId);
  if (element) {
    element.style.display = display ? "block" : "none";
  } else {
    console.error(`Element with ID "${elementId}" not found.`);
  }
}

// Function to clear the input and result fields
function clearFields() {
  const codeInput = document.getElementById("codeInput");
  const fileInput = document.getElementById("fileInput");

  if (codeInput) {
    codeInput.value = "";
    fileInput.value = "";
  } else {
    console.error("Elements with IDs 'codeInput' and/or 'result' not found.");
  }
}


const sidebar = document.querySelector('.sidebar');
const content = document.querySelector('.content');
const supporters = document.querySelector('.supporters');
const h3Supporters = document.querySelector('h3.supporters');
const video = document.getElementById('myVideo');
const textOutput = document.getElementById('textOutput');
const originBodyOverflowY = document.body.style.overflowY;

if (textOutput) {
  const originTextOutputOverflowY = textOutput.style.overflowY;
}

let recordText = "";
let codeType = "";
let processTime = 0;


// 側邊欄展開時觸發事件
sidebar.addEventListener('mouseenter', () => {
    // 添加內容區域的暗化效果
    content.classList.add('content-darkened');
    document.body.style.overflowY = 'hidden'; // 鎖定網頁滾動
    if (textOutput) document.getElementById("textOutput").style.overflowY = "hidden";
});

// 側邊欄縮回時觸發事件
sidebar.addEventListener('mouseleave', () => {
    // 移除內容區域的暗化效果
    content.classList.remove('content-darkened');
    document.body.style.overflowY = originBodyOverflowY; // 解鎖網頁滾動
    if (textOutput && originBodyOverflowY) textOutput.style.overflowY = "auto";
});

if (textOutput){
    textOutput.addEventListener('mouseenter', () => {
        document.body.style.overflowY = 'hidden'; // 解鎖網頁滾動
        textOutput.style.overflowY = "auto";
    });

    textOutput.addEventListener('mouseleave', () => {
        document.body.style.overflowY = 'auto'; // 解鎖網頁滾動
        textOutput.style.overflowY = "hidden";
    });
}

// Function to process code input
function processCodeInput() {
  const codeInput = document.getElementById("codeInput");
  const loader = document.getElementById("loader");
  const blocker = document.getElementById("blocker");
  const loadmsg = document.getElementById("loadmsg");
  const myselect = document.getElementById("myselect");

  if (codeInput && loader && blocker && loadmsg) {
    if (codeInput.value.trim() === "") {
      document.querySelector('.footerdesc').style.display = "flex";
      document.querySelector('.footerdesc').style.backgroundColor = "#f66868";
      document.querySelector('.footerdesc').innerHTML = "No code to run! Please retry.";
      setTimeout(() => {
          document.querySelector('.footerdesc').style.animation = "heightoff 0.75s forwards";
      }, 2000);
      document.querySelector('.footerdesc').style.animation = "heightaddon 0.75s forwards";
    } else {
      recordText = codeInput.value;
      processTime = new Date().getTime();
      toggleVisibility("loader", true);
      toggleVisibility("blocker", true);
      toggleVisibility("loadmsg", true);
      if (window.location.href.includes("modify")){
        codeType = "Modify Code";
        console.log("modify");
        sendDataToAnalyzeServer(codeInput.value);
      }
      else {
        codeType = "Generate Code";
        console.log("generate");
        sendDataToGenerateServer(codeInput.value, myselect.value);
        console.log(myselect.value);
      }
    }
  } else {
    console.error("One or more required elements not found.");
  }
  console.log("ok");
  return;
}


// Function to enhance text input experience
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

  if (keyPairs[event.key]) {
    event.preventDefault();
    const { selectionStart, selectionEnd, value } = element;

    element.value =
      value.substring(0, selectionStart) +
      keyPairs[event.key] +
      value.substring(selectionEnd);
    element.selectionStart = element.selectionEnd = selectionStart + 1;
  }
}

// Function to send code data to the server
function sendDataToAnalyzeServer(code) {
  fetch("http://127.0.0.1:5000/process_code", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ code }),
  })
    .then((response) => response.json())
    .then((data) => {
      const textOutput = document.getElementById("textOutput");
      if (textOutput) {
        toggleVisibility("loader", false);
        toggleVisibility("blocker", false);
        toggleVisibility("loadmsg", false);
        textOutput.value = data.result;
        textOutput.style.display = "flex";
        textOutput.style.border = "1px solid #D0D0D0";
        textOutput.style.backgroundColor = "#0f0f0f";
        textOutput.style.marginBottom = "100px";
        textOutput.style.height = "30%";
        document.getElementById("AImsg").style.display = "block";
        createTicket(data.result);
        document.querySelector('.footerdesc').style.display = "flex";
        document.querySelector('.footerdesc').style.backgroundColor = "#5ae366";
        document.querySelector('.footerdesc').innerHTML = "Analyze Successful.";
        setTimeout(() => {
            document.querySelector('.footerdesc').style.animation = "heightoff 0.75s forwards";
        }, 2000);
        document.querySelector('.footerdesc').style.animation = "heightaddon 0.75s forwards";
      } else {
        console.error("Element with ID 'textOutput' not found.");
      }
    })
    .catch((error) => {
      toggleVisibility("loader", false);
      toggleVisibility("blocker", false);
      toggleVisibility("loadmsg", false);
      console.error("Error:", error);
      document.querySelector('.footerdesc').style.display = "flex";
      document.querySelector('.footerdesc').style.backgroundColor = "#f66868";
      document.querySelector('.footerdesc').innerHTML = "An error occurred while processing the code.";
      setTimeout(() => {
          document.querySelector('.footerdesc').style.animation = "heightoff 0.75s forwards";
      }, 2000);
      document.querySelector('.footerdesc').style.animation = "heightaddon 0.75s forwards";
    });
}

function sendDataToGenerateServer(code, lang) {
    fetch("http://127.0.0.1:5000/gen_code", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ code, lang }),
    })
    .then((response) => response.json())
    .then((data) => {
        const textOutput = document.getElementById("textOutput");
        if (textOutput) {
            toggleVisibility("loader", false);
            toggleVisibility("blocker", false);
            toggleVisibility("loadmsg", false);
            textOutput.value = data.result;
            textOutput.style.display = "flex";
            textOutput.style.border = "1px solid #D0D0D0";
            textOutput.style.backgroundColor = "#0f0f0f";
            textOutput.style.marginBottom = "100px";
            textOutput.style.height = "50%";
            document.getElementById("AImsg").style.display = "block";
            createTicket(data.result, lang);
            document.querySelector('.footerdesc').style.display = "flex";
            document.querySelector('.footerdesc').style.backgroundColor = "#5ae366";
            document.querySelector('.footerdesc').innerHTML = "Generate Successful.";
            setTimeout(() => {
                document.querySelector('.footerdesc').style.animation = "heightoff 0.75s forwards";
            }, 2000);
            document.querySelector('.footerdesc').style.animation = "heightaddon 0.75s forwards";
        } else {
            console.error("Element with ID 'textOutput' not found.");
        }
    })
    .catch((error) => {
        toggleVisibility("loader", false);
        toggleVisibility("blocker", false);
        toggleVisibility("loadmsg", false);
        console.error("Error:", error);
        document.querySelector('.footerdesc').style.display = "flex";
        document.querySelector('.footerdesc').style.backgroundColor = "#f66868";
        document.querySelector('.footerdesc').innerHTML = "An error occurred while processing the code.";
        setTimeout(() => {
          document.querySelector('.footerdesc').style.animation = "heightoff 0.75s forwards";
        }, 2000);
        document.querySelector('.footerdesc').style.animation = "heightaddon 0.75s forwards";
    });
}

// Function to create a ticket

function createTicket(data, lang) {
  let numberseq = localStorage.getItem("numberseq");
  if (numberseq == null) {
    numberseq = 1;
  }
  var ticket = [numberseq, codeType, processTime, (lang ? lang : "N/A")];
  console.log(ticket);
  localStorage.setItem('ticket' + numberseq, ticket);
  localStorage.setItem('record' + numberseq, recordText);
  localStorage.setItem('response' + numberseq, data);
  console.log('ticket' + numberseq);
  numberseq++;
  localStorage.setItem("numberseq", numberseq);
  console.log(numberseq);
}

// Event listeners
const clearButton = document.getElementById("clearButton");
const runButton = document.getElementById("runButton");
const codeInput = document.getElementById("codeInput");
const uploadButton = document.getElementById("uploadButton");

if (clearButton) {
  clearButton.addEventListener("click", clearFields);
} else {
  console.error("Element with ID 'clearButton' not found.");
}

if (runButton) {
  runButton.addEventListener("click", processCodeInput);
} else {
  console.error("Element with ID 'runButton' not found.");
}

if (codeInput) {
  codeInput.addEventListener("keydown", function (e) {
    enhanceTextInput(e, this);
  });
} else {
  console.error("Element with ID 'codeInput' not found.");
}

if (uploadButton) {
  uploadButton.addEventListener("click", function () {
    const codeInput = document.getElementById("codeInput");
    var fileInput = document.getElementById("fileInput");
    var file = fileInput.files[0];
    const availableExtensions = ["txt", "py", "js", "html", "css", "c", "cpp", "java"];

    toggleVisibility("loader", true);
    toggleVisibility("blocker", true);
    toggleVisibility("loadmsg", true);

    if (!file) {
        toggleVisibility("loader", false);
        toggleVisibility("blocker", false);
        toggleVisibility("loadmsg", false);
        document.querySelector('.footerdesc').style.display = "flex";
        document.querySelector('.footerdesc').style.backgroundColor = "#f66868";
        document.querySelector('.footerdesc').innerHTML = "No file selected! Please retry.";
        setTimeout(() => {
            document.querySelector('.footerdesc').style.animation = "heightoff 0.75s forwards";
        }, 2000);
        document.querySelector('.footerdesc').style.animation = "heightaddon 0.75s forwards";
        return;
    }

    var fileName = file.name;
    var fileExtension = fileName.split(".").pop().toLowerCase();

    if (!availableExtensions.includes(fileExtension)) {
        toggleVisibility("loader", false);
        toggleVisibility("blocker", false);
        toggleVisibility("loadmsg", false);
        document.querySelector('.footerdesc').style.display = "flex";
        document.querySelector('.footerdesc').style.backgroundColor = "#f66868";
        document.querySelector('.footerdesc').innerHTML = "Invalid file type! Please retry.";
        setTimeout(() => {
            document.querySelector('.footerdesc').style.animation = "heightoff 0.75s forwards";
        }, 2000);
        document.querySelector('.footerdesc').style.animation = "heightaddon 0.75s forwards";
        return;
    }

    var reader = new FileReader();

    reader.onload = function () {
        codeInput.value = reader.result;
    };

    reader.onerror = function () {
        document.querySelector('.footerdesc').style.display = "flex";
        document.querySelector('.footerdesc').style.backgroundColor = "#f66868";
        document.querySelector('.footerdesc').innerHTML = "Error reading file!";
        setTimeout(() => {
            document.querySelector('.footerdesc').style.animation = "heightoff 0.75s forwards";
        }, 2000);
        document.querySelector('.footerdesc').style.animation = "heightaddon 0.75s forwards";
    };

    reader.readAsText(file);

    fileInput.value = "";
    toggleVisibility("loader", false);
    toggleVisibility("blocker", false);
    toggleVisibility("loadmsg", false);
    document.querySelector('.footerdesc').style.display = "flex";
    document.querySelector('.footerdesc').style.backgroundColor = "#5ae366";
    document.querySelector('.footerdesc').innerHTML = "File uploaded successfully!";
    setTimeout(() => {
        document.querySelector('.footerdesc').style.animation = "heightoff 0.75s forwards";
    }, 2000);
    document.querySelector('.footerdesc').style.animation = "heightaddon 0.75s forwards";
  });
}

