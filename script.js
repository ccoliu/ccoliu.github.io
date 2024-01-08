// Helper function to toggle the visibility of elements
function toggleVisibility(elementId, display) {
  const element = document.getElementById(elementId);
  if (element) {
      element.style.display = display ? "block" : "none";
  }
}

// Function to clear the input and result fields
function clearFields() {
  document.getElementById("codeInput").value = "";
  document.getElementById("result").value = "";
}

// Function to process code input
function processCodeInput() {
  const codeInput = document.getElementById("codeInput");
  const result = document.getElementById("result");

  if (codeInput.value.trim() === "") {
      result.value = "No code to run! Please retry.";
      setTimeout(() => result.value = "", 5000);
  } else {
      toggleVisibility("loader", true);
      toggleVisibility("blocker", true);
      toggleVisibility("loadmsg", true);
      sendDataToServer(codeInput.value);
  }
}

// Function to enhance text input experience
function enhanceTextInput(event, element) {
  const keyPairs = {
      "Tab": "\t",
      "(": "()",
      "{": "{}",
      "[": "[]",
      "\"": "\"\"",
      "'": "''",
      "<": "<>"
  };

  if (keyPairs[event.key]) {
      event.preventDefault();
      const start = element.selectionStart;
      const end = element.selectionEnd;
      const value = element.value;

      element.value = value.substring(0, start) + keyPairs[event.key] + value.substring(end);
      element.selectionStart = element.selectionEnd = start + 1;
  }
}

// Function to send code data to the server
function sendDataToServer(code) {
  fetch('https://whps970083.tplinkdns.com/process_code', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code }),
  })
  .then(response => response.json())
  .then(data => {
      toggleVisibility("loader", false);
      toggleVisibility("blocker", false);
      toggleVisibility("loadmsg", false);
      const textOutput = document.getElementById('textOutput');
      textOutput.value = data.result;
      textOutput.style.display = "flex";
      textOutput.style.border = "1px solid #D0D0D0";
      textOutput.style.backgroundColor = "#0f0f0f";
      textOutput.style.marginBottom = "200px";
      document.getElementById('AImsg').style.display = "block";
      document.getElementById("result").value = "Analyze Successful.";
      setTimeout(() => document.getElementById("result").value = "", 5000);
  })
  .catch(error => {
      toggleVisibility("loader", false);
      toggleVisibility("blocker", false);
      toggleVisibility("loadmsg", false);
      console.error('Error:', error);
      document.getElementById('result').value = "An error occurred while processing the code.";
  });
}

// Event listeners
document.getElementById("clearButton").addEventListener("click", clearFields);
document.getElementById("runButton").addEventListener("click", processCodeInput);
document.getElementById('codeInput').addEventListener('keydown', function(e) {
  enhanceTextInput(e, this);
});
