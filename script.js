document.getElementById("clearButton").addEventListener("click", function() {
  document.getElementById("codeInput").value = "";
  document.getElementById("result").value = "";
});

document.getElementById("runButton").addEventListener("click", function() {
<<<<<<< HEAD
  var code = document.getElementById("codeInput").value;
  if (code == "") {
      document.getElementById("result").value = "No code to run! Please retry.";
  } else {
      document.getElementById("result").value = "Processing...";
      sendDataToServer(code);
=======
    var code = document.getElementById("codeInput").value;
    if (code == "") {
      document.getElementById("result").value = "No code to run! Please retry.";
      setTimeout(function() {
        document.getElementById("result").value = "";
      }  , 5000);
    }
    else
    {
        document.getElementById("result").value = "Processing...";
    }
    sendDataToServer(code);
});

document.getElementById('codeInput').addEventListener('keydown', function(e) {
  if (e.key == 'Tab') {
      e.preventDefault();
      var start = this.selectionStart;
      var end = this.selectionEnd;

      this.value = this.value.substring(0, start) +
          "\t" + this.value.substring(end);

      this.selectionStart =
          this.selectionEnd = start + 1;
  }
  if (e.key == '('){
    e.preventDefault();
    var start = this.selectionStart;
    var end = this.selectionEnd;

    this.value = this.value.substring(0, start) + "()" + this.value.substring(end); 

    this.selectionStart =
        this.selectionEnd = start + 1;
  }
  if (e.key == '{'){
    e.preventDefault();
    var start = this.selectionStart;
    var end = this.selectionEnd;

    this.value = this.value.substring(0, start) + "{}" + this.value.substring(end); 

    this.selectionStart =
        this.selectionEnd = start + 1;
  }
  if (e.key == '['){
    e.preventDefault();
    var start = this.selectionStart;
    var end = this.selectionEnd;

    this.value = this.value.substring(0, start) + "[]" + this.value.substring(end); 

    this.selectionStart =
        this.selectionEnd = start + 1;
  }
  if (e.key == '"'){
    e.preventDefault();
    var start = this.selectionStart;
    var end = this.selectionEnd;

    this.value = this.value.substring(0, start) + '""' + this.value.substring(end); 

    this.selectionStart =
        this.selectionEnd = start + 1;
  }
  if (e.key == "'"){
    e.preventDefault();
    var start = this.selectionStart;
    var end = this.selectionEnd;

    this.value = this.value.substring(0, start) + "''" + this.value.substring(end); 

    this.selectionStart =
        this.selectionEnd = start + 1;
  }
  if (e.key == '<'){
    e.preventDefault();
    var start = this.selectionStart;
    var end = this.selectionEnd;

    this.value = this.value.substring(0, start) + "<>" + this.value.substring(end); 

    this.selectionStart =
        this.selectionEnd = start + 1;
>>>>>>> 36bc73517b570ac2f1941abb2f5649677f24f0e1
  }
});

function sendDataToServer(code) {  
  fetch('https://192.168.0.107:5000/process_code', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code }),
<<<<<<< HEAD
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
=======
    })
    .then(response => response.json())
    .then(data => {
      document.getElementById('resultmsg').style.visibility = "visible";
      document.getElementById('resultmsg').value = data.result;
      document.getElementById("result").value = "Analyze Successful.";
      setTimeout(function() {
        document.getElementById("result").value = "";
      }  , 5000);
    })
    .catch(error => {
>>>>>>> 36bc73517b570ac2f1941abb2f5649677f24f0e1
      console.error('Error:', error);
      document.getElementById('result').value = "An error occurred while processing the code.";
  });
}