
//////////////IP SETTINGS/////////////////////
const GITWEB = "https://140.118.101.66:61911/"
const LOCALWEB = "https://140.118.101.66:61911/"
const LOCALGENERATE = "https://140.118.101.66:56494/"
const GLOBALGENERATE = "https://140.118.101.66:56494/"
currentGenerateServerIP = LOCALGENERATE;
let CURRENTWEB = localStorage.getItem("server") ? localStorage.getItem("server") : LOCALWEB;
/////////////////////////////////////////////
let originalTab = 1;
let exectab = 1;
let temp = "";
let buttonDisabled = false;
let uploadDisabled = false;

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

function clearResponse() {
  const textOutput = document.getElementById("textOutput");
  if (textOutput) {
    textOutput.value = "";
    textOutput.style.height = "0px";
    textOutput.style.display = "none";
  } else {
    console.error("Element with ID 'textOutput' not found.");
  }
  if (document.querySelector('.responseInfo')) {
    document.querySelector('.responseInfo').style.display = "none";
  }
  else
  {
    document.querySelector('.AImsg').style.display = "none";
  }
}

//Function to clear the input and result fields
function clearFields() {
  if (buttonDisabled == true) {
    return;
  }
  const codeInput = document.getElementById("codeInput");
  const fileInput = document.getElementById("fileInput");
  const JobAssignment = document.querySelector('.JobAssignment');

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
  if (JobAssignment) {
    JobAssignment.innerHTML = "";
    executebtn.style.display = "none";
  }
  if (document.querySelector('.myselect'))
  {
    document.querySelector('.myselect').disabled = false;
  }
  if (document.querySelector('.textEnter'))
  {
    document.querySelector('.textEnter').disabled = false;
    document.querySelector('.textEnter').style.filter = "brightness(1)";
  }
  if (document.querySelector('.buttonUpload'))
  {
    document.querySelector('.buttonUpload').style.filter = "brightness(1)";
    document.querySelector('.buttonUpload').style.cursor = "pointer";
  }
  buttonDisabled = false;
  uploadDisabled = false;
  clearResponse();
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
  if (buttonDisabled == true) {
    return;
  }
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



function createNewJobBtn() {
    if (document.querySelector('.JobAdd')) {
      document.querySelector('.JobAdd').remove();
    }
    newdiv = document.createElement('div');
    newdiv.className = "JobAdd";
    newdiv.innerHTML = `
      <span class="material-symbols-outlined">add</span>
      <a class="AddJob">Add New Job...</a>`;
    document.querySelector('.JobAssignment').appendChild(newdiv);
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
  createNewJobBtn();
}

IDs = [];
responses = [];
recordTexts = [];

// Function to send code data to the server
function sendDataToAnalyzeServer(code) {
  IDs = [];
  responses = [];
  let longcode = [];
  recordTexts = [];
  if (originalTab > 0) {
    textareaArray = document.querySelectorAll('.Inputarea textarea');
    textareaArray.forEach(element => {
      if (element.value != ""){
        longcode.push(element.value);
        recordTexts.push(element.value);
        recordText += element.value + "\n";
      }
    });
  }
  console.log(recordTexts);
  fetch(CURRENTWEB + "process_code", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ longcode }),
  })
    .then((response) => response.json())
    .then((data) => {
      for (let i=0;i<Object.values(data)[0].length;i++){
        IDs.push(Object.values(data)[0][i].id);
        responses.push(Object.values(data)[0][i].optimizedCode + "\n\n" + Object.values(data)[0][i].summary);
      }
      exectab = IDs.length;
      currentTab = 1;
      document.querySelector('.tabInfo').innerHTML = "Tab " + currentTab.toString();
      const textOutput = document.getElementById("textOutput");
      if (textOutput) {
        textOutput.value = responses[0];
        textOutput.style.display = "flex";
        textOutput.style.border = "1px solid #D0D0D0";
        textOutput.style.backgroundColor = "#0f0f0f";
        textOutput.style.marginBottom = "100px";
        textOutput.style.height = "30%";
        createAnalyzeTicket(responses, IDs);
        document.querySelector('.footerdesc').style.display = "flex";
        document.querySelector('.footerdesc').style.backgroundColor = "#5ae366";
        document.querySelector('.footerdesc').innerHTML = "Analyze Successful.";
        setTimeout(() => {
            document.querySelector('.footerdesc').style.animation = "heightoff 0.75s forwards";
        }, 2000);
        document.querySelector('.footerdesc').style.animation = "heightaddon 0.75s forwards";
        document.querySelector('.responseInfo').style.display = "flex";
        document.querySelector('.AImsg').style.display = "block";
        document.getElementById('arrowleft').style.filter = "brightness(0.4)";
        document.getElementById('arrowleft').style.cursor = "not-allowed";
        if (originalTab == 1) {
          document.getElementById('arrowright').style.filter = "brightness(0.4)";
          document.getElementById('arrowright').style.cursor = "not-allowed";
        }
        else {
          document.getElementById('arrowright').style.filter = "brightness(1)";
          document.getElementById('arrowright').style.cursor = "pointer";
        }
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
      recordText = "";
      document.querySelector('.loadinggif').style.display = "none";
    })
}

function sendDataToGenerateServer(code, lang) {
    recordText = code;
    temp = code;
    uploadDisabled = true;
    document.querySelector('.myselect').disabled = true;
    document.querySelector('.textEnter').disabled = true;
    document.querySelector('.textEnter').style.filter = "brightness(0.5)";
    document.querySelector('.buttonUpload').style.cursor = "not-allowed";
    document.querySelector('.buttonUpload').style.filter = "brightness(0.5)";
    fetch(currentGenerateServerIP + "gen_code", {
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
        document.querySelector('.myselect').disabled = false;
    })
    .finally(() => {
      document.querySelector('.loadinggif').style.display = "none";
    })
}

// Function to create a ticket

function createTicket(data, id, lang) {
  console.log(recordText);
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

function createAnalyzeTicket(responses, ids, lang) {
  console.log(recordText);
  let numberseq = localStorage.getItem("numberseq");
  if (numberseq == null) {
    numberseq = 1;
  }
  for (let i=0;i<responses.length;i++){
    var ticket = [numberseq, codeType, processTime, (lang ? lang : "N/A")];
    console.log(ticket);
    localStorage.setItem('ticket' + numberseq, ticket);
    localStorage.setItem('record' + numberseq, recordTexts[i]);
    localStorage.setItem('response' + numberseq, responses[i]);
    localStorage.setItem('id' + numberseq, ids[i]);
    console.log('ticket' + numberseq);
    numberseq++;
    localStorage.setItem("numberseq", numberseq);
  }
  console.log(numberseq);
}

// Event listeners
const clearButton = document.getElementById("clearButton");
const runButton = document.getElementById("runButton");
const codeInput = document.querySelector(".Inputarea");
const uploadButton = document.getElementById("uploadButton");

if (clearButton && !buttonDisabled) {
  clearButton.addEventListener("click", clearFields);
} else {
  console.error("Element with ID 'clearButton' not found.");
}

if (runButton && !buttonDisabled) {
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
        //console.log('.textEnter' + filenum.toString());
        if (document.querySelector('.textEnter' + filenum.toString()).value != "") {
          filenum++;
          processFile(file, filenum);
        }
        else{
          document.querySelector('.textEnter' + filenum.toString()).value = reader.result;
        }
        //console.log(document.querySelector('.textEnter' + filenum.toString()).value);
        resolve();
      }
      reader.onerror = reject;
      reader.readAsText(file);
    });
  }

  uploadButton.addEventListener("click", function () {
    if (uploadDisabled == true) {
      return;
    }
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
    currentGenerateServerIP = GLOBALGENERATE;
  } else {
    CURRENTWEB = LOCALWEB;
    currentGenerateServerIP = LOCALWEB;
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
    if (event.target.matches('.abortbtn') || event.target.matches('.Jobbtn')) {
      if (!buttonDisabled)
      {
        targetedTab = event.target.closest('.JobAssign');
        targetedTab.remove();
      }
    }
    else if (event.target.matches('.JobAdd') || event.target.matches('.JobAdd *')) {
      if (buttonDisabled == true) {
        return;
      }
      newdiv = document.createElement('div');
      newdiv.className = 'JobAssign';
      newdiv.innerHTML = `
        <div class="Jobtitle">
                      <textarea class="AssignTitle" placeholder="Add new job assignment here..."></textarea>
                  </div>
                  <div class="Jobbtn">
                      <a class="abortbtn">Abort</a>
        </div>`;
      document.querySelector('.JobAssignment').appendChild(newdiv);
      createNewJobBtn();
      analysisapply();
    }
  });
}

function analysisapply() {
  let textareas = document.querySelectorAll('.AssignTitle');
  textareas.forEach(textarea => {
    textarea.style.height = (1 + (textarea.value.length) / 32) * 14 + 'px';
    if (textarea.value == "") {
      textarea.style.height = '54px';
    }
    textarea.addEventListener('input', autoResize, false);
  });
}

function abortbtnDisable(bool) {
  if (bool == true) {
    let abortbtns = document.querySelectorAll('.abortbtn');
    abortbtns.forEach(abortbtn => {
      abortbtn.parentElement.style.cursor = "not-allowed";
      abortbtn.style.cursor = "not-allowed";
      abortbtn.style.filter = "brightness(0.5)";
    });
  }
  else {
    let abortbtns = document.querySelectorAll('.abortbtn');
    abortbtns.forEach(abortbtn => {
      abortbtn.parentElement.style.cursor = "pointer";
      abortbtn.style.cursor = "pointer";
      abortbtn.style.filter = "brightness(1)";
    });
  }
}

const executebtn = document.querySelector('.buttonExecute');
if (executebtn) {
  executebtn.addEventListener('click', () => {
    recordText = temp;
    buttonDisabled = true;
    document.querySelector('.buttonClear').style.cursor = "not-allowed";
    document.querySelector('.buttonClear').style.filter = "brightness(0.5)";
    document.querySelector('.buttonAnalyse').style.cursor = "not-allowed";
    document.querySelector('.buttonAnalyse').style.filter = "brightness(0.5)";
    document.querySelector('.JobAdd').style.cursor = "not-allowed";
    document.querySelector('.JobAdd').style.filter = "brightness(0.5)";
    abortbtnDisable(true);
    document.querySelector('.myselect').disabled = true;
    let textareaIsEmpty = true;
    let textareas = document.querySelectorAll('.AssignTitle');
    let steps = [];
    textareas.forEach(textarea => {
      if (textarea.value != "") {
        textareaIsEmpty = false;
      }
      steps.push(textarea.value);
    });
    if (textareaIsEmpty || textareas.length == 0) {
      document.querySelector('.footerdesc').style.display = "flex";
      document.querySelector('.footerdesc').style.backgroundColor = "#f66868";
      document.querySelector('.footerdesc').innerHTML = "No job assignment to execute or job assignments are empty! Please retry.";
      setTimeout(() => {
          document.querySelector('.footerdesc').style.animation = "heightoff 0.75s forwards";
      }, 2000);
      document.querySelector('.footerdesc').style.animation = "heightaddon 0.75s forwards";
      return;
    }
    console.log(steps);
    document.querySelector('.loadinggif2').style.display = "flex";
    fetch(currentGenerateServerIP + "execute_steps", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ steps }),
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
        createTicket(data.result, data.id);
        document.getElementById("AImsg").style.display = "block";
        document.querySelector('.footerdesc').style.display = "flex";
        document.querySelector('.footerdesc').style.backgroundColor = "#5ae366";
        document.querySelector('.footerdesc').innerHTML = "Execute Successful.";
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
      recordText = "";
      buttonDisabled = false;
      document.querySelector('.buttonClear').style.cursor = "pointer";
      document.querySelector('.buttonClear').style.filter = "brightness(1)";
      document.querySelector('.buttonAnalyse').style.cursor = "pointer";
      document.querySelector('.buttonAnalyse').style.filter = "brightness(1)";
      document.querySelector('.JobAdd').style.cursor = "pointer";
      document.querySelector('.JobAdd').style.filter = "brightness(1)";
      abortbtnDisable(false);
      document.querySelector('.loadinggif2').style.display = "none";
    });
  })
}

const buttonleftarrow = document.getElementById('arrowleft');
const buttonrightarrow = document.getElementById('arrowright');
let currentTab = 1;

if (buttonleftarrow) {
  buttonleftarrow.addEventListener('click', () => {
    currentTab--;
    if (currentTab < 1) {
      currentTab = 1;
      return;
    }
    if (currentTab == 1) {
      buttonleftarrow.style.cursor = "not-allowed";
      buttonleftarrow.style.filter = "brightness(0.4)";
    }
    if (currentTab < exectab) {
      buttonrightarrow.style.cursor = "pointer";
      buttonrightarrow.style.filter = "brightness(1)";
    }
    document.querySelector('.tabInfo').innerHTML = "Tab " + currentTab.toString();
    textOutput.value = responses[currentTab - 1];
  });
}

if (buttonrightarrow) {
  buttonrightarrow.addEventListener('click', () => {
    currentTab++;
    if (currentTab > exectab) {
      currentTab = originalTab;
      return;
    }
    if (currentTab == exectab) {
      buttonrightarrow.style.cursor = "not-allowed";
      buttonrightarrow.style.filter = "brightness(0.4)";
    }
    if (currentTab > 1) {
      buttonleftarrow.style.cursor = "pointer";
      buttonleftarrow.style.filter = "brightness(1)";
    }
    document.querySelector('.tabInfo').innerHTML = "Tab " + currentTab.toString();
    textOutput.value = responses[currentTab - 1];
  });
}