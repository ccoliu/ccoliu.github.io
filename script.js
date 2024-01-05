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
      document.getElementById("loader").style.display = "block";
      document.getElementById("blocker").style.display = "block";
      document.getElementById('loadmsg').style.display = "block";
      sendDataToServer(code);
    }
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
  fetch('https://whps970083.tplinkdns.com/process_code', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code }),
    })
    .then(response => response.json())
    .then(data => {
      document.getElementById("loader").style.display = "none";
      document.getElementById("blocker").style.display = "none";
      document.getElementById('loadmsg').style.display = "none";
      document.getElementById('textOutput').value = data.result;
      document.getElementById('textOutput').style.display = "flex";
      document.getElementById('textOutput').style.border = "1px solid #D0D0D0";
      document.getElementById('textOutput').style.backgroundColor = "#0f0f0f";
      document.getElementById('textOutput').style.marginBottom = "200px"
      document.getElementById('AImsg').style.display = "block";
      document.getElementById("result").value = "Analyze Successful.";
      setTimeout(function() {
        document.getElementById("result").value = "";
      }  , 5000);
    })
    .catch(error => {
      document.getElementById("loader").style.display = "none";
      document.getElementById("blocker").style.display = "none";
      document.getElementById('loadmsg').style.display = "none";
      console.error('Error:', error);
      document.getElementById('result').value = "An error occurred while processing the code.";
  });
}