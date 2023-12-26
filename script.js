document.getElementById("clearButton").addEventListener("click", function() {
    document.getElementById("codeInput").value = "";
    document.getElementById("result").value = "";
});

document.getElementById("runButton").addEventListener("click", function() {
    var code = document.getElementById("codeInput").value;
    if (code == "") {
        document.getElementById("result").value = "No code to run! Please retry.";
    }
    else
    {
        document.getElementById("result").value = "Processing...";
    }
});

document.getElementById("result").addEventListener("input", function() {
    var code = document.getElementById("codeInput").value;
    if (document.getElementById("result").value.length == 1) {
        document.getElementById("result").value = "";
    }
    else if (code == "") {
        document.getElementById("result").value = "No code to run! Please retry.";
    }
    else
    {
        document.getElementById("result").value = "Processing...";
    }
});
