document.getElementById("clearButton").addEventListener("click", function() {
    document.getElementById("codeInput").value = "";
    document.getElementById("result").value = "";
});

document.getElementById("runButton").addEventListener("click", function() {
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
  }
});

function sendDataToServer(code) {  
    fetch('http://192.168.0.107:5000/process_code', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code }),
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
      console.error('Error:', error);
    });
  }