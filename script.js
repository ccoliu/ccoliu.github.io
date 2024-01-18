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
  const result = document.getElementById("result");
  const fileInput = document.getElementById("fileInput");

  if (codeInput && result) {
    codeInput.value = "";
    result.value = "";
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
// 側邊欄展開時觸發事件
sidebar.addEventListener('mouseenter', () => {
    // 添加內容區域的暗化效果
    content.classList.add('content-darkened');
    supporters.style.display = 'block'; // 顯示 supporters
});

// 側邊欄縮回時觸發事件
sidebar.addEventListener('mouseleave', () => {
    // 移除內容區域的暗化效果
    content.classList.remove('content-darkened');
    supporters.style.display = 'none'; // 隱藏 supporters
});



// Function to process code input
function processCodeInput() {
  const codeInput = document.getElementById("codeInput");
  const result = document.getElementById("result");
  const loader = document.getElementById("loader");
  const blocker = document.getElementById("blocker");
  const loadmsg = document.getElementById("loadmsg");

  if (codeInput && result && loader && blocker && loadmsg) {
    if (codeInput.value.trim() === "") {
      result.value = "No code to run! Please retry.";
      setTimeout(() => (result.value = ""), 5000);
    } else {
      toggleVisibility("loader", true);
      toggleVisibility("blocker", true);
      toggleVisibility("loadmsg", true);
      sendDataToServer(codeInput.value);
    }
  } else {
    console.error("One or more required elements not found.");
  }
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
function sendDataToServer(code) {
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
        textOutput.style.marginBottom = "200px";
        document.getElementById("AImsg").style.display = "block";
        document.getElementById("result").value = "Analyze Successful.";
        setTimeout(() => (document.getElementById("result").value = ""), 5000);
      } else {
        console.error("Element with ID 'textOutput' not found.");
      }
    })
    .catch((error) => {
      toggleVisibility("loader", false);
      toggleVisibility("blocker", false);
      toggleVisibility("loadmsg", false);
      console.error("Error:", error);
      document.getElementById("result").value =
        "An error occurred while processing the code.";
    });
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
    const result = document.getElementById("result");
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
        result.value = "No file selected! Please retry.";
        setTimeout(() => (result.value = ""), 5000);
        return;
    }

    var fileName = file.name;
    var fileExtension = fileName.split(".").pop().toLowerCase();

    if (!availableExtensions.includes(fileExtension)) {
        toggleVisibility("loader", false);
        toggleVisibility("blocker", false);
        toggleVisibility("loadmsg", false);
        result.value = "Invalid file type! Please retry.";
        setTimeout(() => (result.value = ""), 5000);
        return;
    }

    var reader = new FileReader();

    reader.onload = function () {
        codeInput.value = reader.result;
    };

    reader.onerror = function () {
        result.value = "Error reading file!";
        setTimeout(() => (result.value = ""), 5000);
    };

    reader.readAsText(file);

    result.value = "File uploaded successfully!";
    fileInput.value = "";
    toggleVisibility("loader", false);
    toggleVisibility("blocker", false);
    toggleVisibility("loadmsg", false);
    setTimeout(() => (result.value = ""), 5000);
  });
}