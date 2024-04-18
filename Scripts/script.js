// const { text } = require("stream/consumers");

//////////////IP SETTINGS/////////////////////
const GITWEB = "https://140.118.184.235:5000/"
const LOCALWEB = "http://127.0.0.1:5000/"
let CURRENTWEB = localStorage.getItem("server") ? localStorage.getItem("server") : LOCALWEB;
/////////////////////////////////////////////
let originalTab = 1;

window.onload = function() {
  serverText = document.querySelector('.server');
  serverText.innerHTML = "Server: " + (CURRENTWEB == LOCALWEB ? "Local" : "Camp");
}



// Helper function to toggle the visibility of elements
function toggleVisibility(elementId, display) {
  const element = document.getElementById(elementId);
  if (element) {
    element.style.display = display ? "block" : "none";
  } else {
    console.error(`Element with ID "${elementId}" not found.`);
  }
}

//Function to clear the input and result fields
function clearFields() {
  const codeInput = document.getElementById("codeInput");
  const fileInput = document.getElementById("fileInput");

  if (codeInput) {
    codeInput.value = "";
    if (originalTab > 1)
    {
      textareaArray = document.querySelectorAll('.Inputarea textarea');
        textareaArray.forEach(element => {
          element.value = ""
        });
    }
    fileInput.value = "";
  } else {
    console.error("Elements with IDs 'codeInput' and/or 'result' not found.");
  }
}

const newtab = document.querySelector('.Addnewtab');
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
    sidebar.scrollTo({ top: 0, behavior: 'smooth' });
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
  const myselect = document.getElementById("myselect");

  if (codeInput) {
    if (codeInput.value.trim() === "") {
      document.querySelector('.footerdesc').style.display = "flex";
      document.querySelector('.footerdesc').style.backgroundColor = "#f66868";
      document.querySelector('.footerdesc').innerHTML = "No code to run! Please retry.";
      setTimeout(() => {
          document.querySelector('.footerdesc').style.animation = "heightoff 0.75s forwards";
      }, 2000);
      document.querySelector('.footerdesc').style.animation = "heightaddon 0.75s forwards";
    } else {
      processTime = new Date().getTime();
      document.querySelector('.loadinggif').style.display = "flex";
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

function JobAdd(data) {
  document.querySelector('.JobAssignment').innerHTML = "";
  for (let i=0;i<Object.values(data)[0].length;i++)
  {
    newdiv = document.createElement('div');
    newdiv.className = "JobAssign";
    newdiv.innerHTML = `
      <div class="Jobtitle">
                    <textarea class="AssignTitle">${Object.values(data)[0][i]}</textarea>
                </div>
                <div class="Jobbtn">
                    <a class="abortbtn">Abort</a>
                </div>`;
    document.querySelector('.JobAssignment').appendChild(newdiv);
    analysisapply();
  }
  // for(let i=0;i<data.length;i++)
  // {
    
  // }
}

// Function to send code data to the server
function sendDataToAnalyzeServer(code) {
  let longcode = "";
  if (originalTab > 1) {
    textareaArray = document.querySelectorAll('.Inputarea textarea');
    textareaArray.forEach(element => {
      if (element.value != ""){
        longcode += element.value + "\n\n";
      }
    });
    code = longcode + '\b';
  }
  recordText = code;
  console.log(code);
  fetch(CURRENTWEB + "process_code", {
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
        textOutput.value = data.result;
        textOutput.style.display = "flex";
        textOutput.style.border = "1px solid #D0D0D0";
        textOutput.style.backgroundColor = "#0f0f0f";
        textOutput.style.marginBottom = "100px";
        textOutput.style.height = "30%";
        document.getElementById("AImsg").style.display = "block";
        createTicket(data.result, data.id);
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
      console.error("Error:", error);
      document.querySelector('.footerdesc').style.display = "flex";
      document.querySelector('.footerdesc').style.backgroundColor = "#f66868";
      document.querySelector('.footerdesc').innerHTML = "An error occurred while processing the code.";
      setTimeout(() => {
          document.querySelector('.footerdesc').style.animation = "heightoff 0.75s forwards";
      }, 2000);
      document.querySelector('.footerdesc').style.animation = "heightaddon 0.75s forwards";
    })
    .finally(() => {
      document.querySelector('.loadinggif').style.display = "none";
    })
}

function sendDataToGenerateServer(code, lang) {
    recordText = code;
    fetch(CURRENTWEB + "gen_code", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ code, lang }),
    })
    .then((response) => response.json())
    .then((data) => {
        const textOutput = document.getElementById("textOutput");
        console.log(typeof(data));
        JobAdd(data);
        if (textOutput) {
            // textOutput.value = "";
            // textOutput.style.display = "flex";
            // textOutput.style.border = "1px solid #D0D0D0";
            // textOutput.style.backgroundColor = "#0f0f0f";
            // textOutput.style.marginBottom = "100px";
            // textOutput.style.height = "50%";
            // document.getElementById("AImsg").style.display = "block";
            // createTicket(data.result, data.id, lang);
            document.querySelector('.footerdesc').style.display = "flex";
            document.querySelector('.footerdesc').style.backgroundColor = "#5ae366";
            document.querySelector('.footerdesc').innerHTML = "Generate Successful.";
            setTimeout(() => {
                document.querySelector('.footerdesc').style.animation = "heightoff 0.75s forwards";
            }, 2000);
            document.querySelector('.footerdesc').style.animation = "heightaddon 0.75s forwards";
            document.querySelector('.buttonExecute').style.display = "flex";
        } else {
            console.error("Element with ID 'textOutput' not found.");
        }
    })
    .catch((error) => {
        console.error("Error:", error);
        document.querySelector('.footerdesc').style.display = "flex";
        document.querySelector('.footerdesc').style.backgroundColor = "#f66868";
        document.querySelector('.footerdesc').innerHTML = "An error occurred while processing the code.";
        setTimeout(() => {
          document.querySelector('.footerdesc').style.animation = "heightoff 0.75s forwards";
        }, 2000);
        document.querySelector('.footerdesc').style.animation = "heightaddon 0.75s forwards";
    })
    .finally(() => {
      document.querySelector('.loadinggif').style.display = "none";
    })
}

// Function to create a ticket

function createTicket(data, id, lang) {
  let numberseq = localStorage.getItem("numberseq");
  if (numberseq == null) {
    numberseq = 1;
  }
  var ticket = [numberseq, codeType, processTime, (lang ? lang : "N/A")];
  console.log(ticket);
  localStorage.setItem('ticket' + numberseq, ticket);
  localStorage.setItem('record' + numberseq, recordText);
  localStorage.setItem('response' + numberseq, data);
  localStorage.setItem('id' + numberseq, id);
  console.log('ticket' + numberseq);
  numberseq++;
  localStorage.setItem("numberseq", numberseq);
  console.log(numberseq);
}

// Event listeners
const clearButton = document.getElementById("clearButton");
const runButton = document.getElementById("runButton");
const codeInput = document.querySelector(".Inputarea");
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
  codeInput.addEventListener("keydown", function (event) {
    if (event.target.matches("textarea")) {
      enhanceTextInput(event, event.target);
    }
  });
}

if (uploadButton) {

  async function processFile(file, filenum) {
    return new Promise((resolve, reject) => {
      var reader = new FileReader();
      reader.onload = () => {
        if (originalTab < filenum) {
            document.querySelector('.Addnewtab').click();
        }
        console.log('.textEnter' + filenum.toString());
        document.querySelector('.textEnter' + filenum.toString()).value = reader.result;
        console.log(document.querySelector('.textEnter' + filenum.toString()).value);
        resolve();
      }
      reader.onerror = reject;
      reader.readAsText(file);
    });
  }

  uploadButton.addEventListener("click", function () {
    filenum = 1;
    errorpop = false;
    var fileInput = document.querySelector(".inputfile");
    var files = Array.from(fileInput.files);
    const availableExtensions = ["txt", "py", "js", "html", "css", "c", "cpp", "java","h"];

    if (files.length == 0) {
      document.querySelector('.footerdesc').style.display = "flex";
      document.querySelector('.footerdesc').style.backgroundColor = "#f66868";
      document.querySelector('.footerdesc').innerHTML = "No file selected! Please retry.";
      setTimeout(() => {
          document.querySelector('.footerdesc').style.animation = "heightoff 0.75s forwards";
      }, 2000);
      document.querySelector('.footerdesc').style.animation = "heightaddon 0.75s forwards";
      return;
    }

    for (let i = 0; i < files.length; i++) {

      if (!files[i]) {
        document.querySelector('.footerdesc').style.display = "flex";
        document.querySelector('.footerdesc').style.backgroundColor = "#f66868";
        document.querySelector('.footerdesc').innerHTML = "No file selected! Please retry.";
        setTimeout(() => {
            document.querySelector('.footerdesc').style.animation = "heightoff 0.75s forwards";
        }, 2000);
        document.querySelector('.footerdesc').style.animation = "heightaddon 0.75s forwards";
        return;
    }

    var fileName = files[i].name;
    var fileExtension = fileName.split(".").pop().toLowerCase();

    if (!availableExtensions.includes(fileExtension)) {
        errorpop = true;
        document.querySelector('.footerdesc').style.display = "flex";
        document.querySelector('.footerdesc').style.backgroundColor = "#f66868";
        document.querySelector('.footerdesc').innerHTML = "\"" + fileName + "\"" + " is invalid file type! Please retry.";
        setTimeout(() => {
            document.querySelector('.footerdesc').style.animation = "heightoff 0.75s forwards";
        }, 2000);
        document.querySelector('.footerdesc').style.animation = "heightaddon 0.75s forwards";
        continue;
    }
    console.log(fileName);
    processFile(files[i], filenum).then(() => {})
    .catch(() => {
        document.querySelector('.footerdesc').style.display = "flex";
        document.querySelector('.footerdesc').style.backgroundColor = "#f66868";
        document.querySelector('.footerdesc').innerHTML = "An error occurred while processing the file.";
        setTimeout(() => {
            document.querySelector('.footerdesc').style.animation = "heightoff 0.75s forwards";
        }, 2000);
        document.querySelector('.footerdesc').style.animation = "heightaddon 0.75s forwards";
        return;
    });
    filenum++;
    }
    
    if (!errorpop) {
      document.querySelector('.footerdesc').style.display = "flex";
      document.querySelector('.footerdesc').style.backgroundColor = "#5ae366";
      document.querySelector('.footerdesc').innerHTML = "File uploaded successfully!";
      setTimeout(() => {
          document.querySelector('.footerdesc').style.animation = "heightoff 0.75s forwards";
      }, 2000);
      document.querySelector('.footerdesc').style.animation = "heightaddon 0.75s forwards";
    }
    fileInput.value = "";
  });
}


let serverText = document.querySelector('.server');

serverText.addEventListener('click', () => {
  if (CURRENTWEB == LOCALWEB) {
    CURRENTWEB = GITWEB;
  } else {
    CURRENTWEB = LOCALWEB;
  }
  localStorage.setItem("server", CURRENTWEB);
  window.location.reload();
});

if (newtab) {
  newtab.addEventListener('click', () => {
    originalTab++;
    newtext = document.createElement('textarea');
    newdiv = document.createElement('div');
    newdiv.className = 'tabWindow' + originalTab.toString();
    newdiv.innerHTML = `
      <p class="tabSeq">Tab${originalTab}</p>
      <span class="material-symbols-outlined" id='crossbutton'>close</span>`;
    newtext.className = 'textEnter' + originalTab.toString();
    newtext.id = 'codeInput';
    newtext.placeholder = 'add your subprogram here...'
    document.querySelector('.Inputarea').appendChild(newdiv);
    document.querySelector('.Inputarea').appendChild(newtext);
  });
}

if (document.querySelector('.Inputarea')) {
  document.querySelector('.Inputarea').addEventListener('click', function(event) {
    if (event.target.matches('.material-symbols-outlined') && event.target.innerHTML == 'close') {
      targetedTab = event.target.closest('.material-symbols-outlined').parentElement;
      backnumber = targetedTab.className[targetedTab.className.length - 1];
      targetedTab.remove();
      console.log('.textEnter' + backnumber);
      let textEnterElement = document.querySelector('.textEnter' + backnumber);
      textEnterElement.remove();
      originalTab--;
      if (parseInt(backnumber) != originalTab + 1) {
        for (let i = parseInt(backnumber) + 1; i <= originalTab + 1; i++) {
          document.querySelector('.tabWindow' + i.toString()).querySelector('.tabSeq').innerHTML = 'Tab' + (i - 1).toString();
          document.querySelector('.tabWindow' + i.toString()).className = 'tabWindow' + (i - 1).toString();
          document.querySelector('.textEnter' + i.toString()).className = 'textEnter' + (i - 1).toString();
        }
      }
    }
  });
}

function autoResize() {
  this.style.height = 'auto';
  this.style.height = this.scrollHeight + 'px';
}

if (document.querySelector('.JobAssignment')) {
  document.querySelector('.JobAssignment').addEventListener('click', function(event) {
    if (event.target.matches('.abortbtn')) {
      targetedTab = event.target.closest('.JobAssign');
      targetedTab.remove();
    }
  });
}

function analysisapply() {
  let textareas = document.querySelectorAll('.AssignTitle');
  textareas.forEach(textarea => {
    textarea.style.height = (1 + (textarea.value.length) / 32) * 14 + 'px';
    textarea.addEventListener('input', autoResize, false);
  });
}