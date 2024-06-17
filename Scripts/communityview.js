const yesBtn = document.querySelector('.yesbtn');
let yesBtnClicked = false;

const noBtn = document.querySelector('.nobtn');
let noBtnClicked = false;

const sendBtn = document.querySelector('.sendbtn');

let buttonFirstClicked = false;

const ticketID = document.querySelector('.ticketID');
const ticketDesc = document.querySelector('.ticketDesc');
const AIresp = document.querySelector('.AIresp');
const tickettype = document.querySelector('.tickettype');
const ticketlang = document.querySelector('.ticketLang');


function createErrorMsg(str){
    document.querySelector('.footerdesc').style.display = "flex";
    document.querySelector('.footerdesc').style.backgroundColor = "#f66868";
    document.querySelector('.footerdesc').innerHTML = str;
    setTimeout(() => {
      document.querySelector('.footerdesc').style.animation = "heightoff 0.75s forwards";
    }, 2000);
    document.querySelector('.footerdesc').style.animation = "heightaddon 0.75s forwards";
    return;
}

function sendCode(dataChunk) {
    console.log(dataChunk);
    let rate = dataChunk.rate;
    let comment = dataChunk.comment;
    let id = dataChunk.id;
    setTimeout(() => {
        fetch(GITWEB + 'viewer_comment', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({rate, comment, id}),
    })
    }, 3500);
    setTimeout(() => {
        window.location.reload();
    }, 3500)
}

window.onload = () => {
    // serverText = document.querySelector('.server');
    // serverText.innerHTML = "Server: " + (CURRENTWEB == LOCALWEB ? "Local" : "Camp");

    let location = window.location.href;
    locationsplit = location.split('?=')[1];
    if (locationsplit == undefined) {
        window.location.href = "community.html";
    }
    else {
        console.log(locationsplit);
    }
    fetch(GITWEB + "viewData", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(locationsplit)
    })
    .then((response) => response.json())
    .then((data) => {
        console.log(data);
        console.log(data['lang']);
        ticketID.innerHTML = data['id'];
        ticketDesc.innerHTML = data['original'];
        AIresp.innerHTML = data['output'] + '\n\n' + data['summary'];
        tickettype.innerHTML = data['mode'].charAt(0).toUpperCase() + data['mode'].slice(1);
        if (data['lang'] !== "undefined") {
            ticketlang.innerHTML = data['lang'];
        }
        else {
            ticketlang.style.display = "none";
            document.querySelector('.codeLang').style.display = "none";
        }
    })
    .catch((error) => {
        createErrorMsg(error);
        return;
    })

    hasCommented = localStorage.getItem('commentPosted' + locationsplit);
    if (hasCommented == 'true') {
        document.querySelector('.Youropinion').innerHTML = "Thank you for your feedback!";
        document.querySelector('.Youropinion').style.display = "flex";
        document.querySelector('.Youropinion').style.justifyContent = "center";
        document.querySelector('.Youropinion').style.alignItems = "center";
        document.querySelector('.Youropinion').style.marginLeft = "0px"; //set margin left to 0
        document.querySelector('.yesbtn').style.display = "none";
        document.querySelector('.nobtn').style.display = "none";
    }
}

function ButtonReturn(button) {
    button.style.backgroundColor = "transparent";
    button.style.border = "1px solid #D0D0D0";
}

yesBtn.addEventListener('click', () => {
    if (buttonFirstClicked == false) {
        document.querySelector('.comment').style.display = "block";
        document.querySelector('.sendbtncontent').style.display = "flex";
        setTimeout(() => window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' }), 500);
        buttonFirstClicked = true;
    }
    yesBtn.style.backgroundColor = "#5ae366";
    yesBtn.style.border = "1px solid #5ae366";
    yesBtnClicked = true;
    if (noBtnClicked) {
        ButtonReturn(noBtn);
        noBtnClicked = false;
    }
});

noBtn.addEventListener('click', () => {
    if (buttonFirstClicked == false) {
        document.querySelector('.comment').style.display = "block";
        document.querySelector('.sendbtncontent').style.display = "flex";
        setTimeout(() => window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' }), 500);
        buttonFirstClicked = true;
    }
    noBtn.style.backgroundColor = "#f66868";
    noBtn.style.border = "1px solid #f66868";
    noBtnClicked = true;
    if (yesBtnClicked) {
        ButtonReturn(yesBtn);
        yesBtnClicked = false;
    }
});

sendBtn.addEventListener('click', () => {
    let comment = document.querySelector('.comment')
    if (comment.value == "") {
        comment.style.border = "1px solid #f66868";
        setTimeout(() => {
            comment.style.border = "1px solid #818181";
        }, 2000);
        document.querySelector('.footerdesc').style.display = "flex";
        document.querySelector('.footerdesc').style.backgroundColor = "#f66868";
        document.querySelector('.footerdesc').innerHTML = "Please write a comment!";
        setTimeout(() => {
            document.querySelector('.footerdesc').style.animation = "heightoff 0.75s forwards";
        }, 2000);
        document.querySelector('.footerdesc').style.animation = "heightaddon 0.75s forwards";
        return;
    }
    else
    { //rate comment id
        const chosedID = document.querySelector('.ticketID').innerHTML; //id
        const YesNo = (yesBtnClicked ? "No problem" : "Something's wrong");
        const userComment = comment.value;

        document.querySelector('.footerdesc').style.display = "flex";
        document.querySelector('.footerdesc').style.backgroundColor = "#5ae366";
        document.querySelector('.footerdesc').innerHTML = "Comment sent! the page will be reloaded later....";
        setTimeout(() => {
            document.querySelector('.footerdesc').style.animation = "heightoff 0.75s forwards";
        }, 2000);
        document.querySelector('.footerdesc').style.animation = "heightaddon 0.75s forwards";

        const dataChunk = {
            "rate": YesNo,
            "comment": userComment,
            "id": chosedID
        }

        sendCode(dataChunk);
        localStorage.setItem('commentPosted' + document.querySelector('.ticketID').innerHTML , 'true');
    }

    return;
});