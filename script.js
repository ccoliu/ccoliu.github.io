document.getElementById("clearButton").addEventListener("click", function() {
  document.getElementById("codeInput").value = "";
  document.getElementById("result").value = "";
});

document.getElementById("runButton").addEventListener("click", function() {
  var code = document.getElementById("codeInput").value;
  if (code == "") {
      document.getElementById("result").value = "No code to run! Please retry.";
  } else {
      document.getElementById("result").value = "Processing...";
      sendDataToServer(code);
  }
});

function sendDataToServer(code) {  
  fetch('https://192.168.0.107:5000/process_code', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code }),
  })
  .then(response => {
      if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
  })
  .then(data => {
      document.getElementById('codeInput').value = data.result;
      document.getElementById('result').value = "Analyzed successfully";
  })
  .catch(error => {
      console.error('Error:', error);
      document.getElementById('result').value = "An error occurred while processing the code.";
  });
}