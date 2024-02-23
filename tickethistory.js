
const yesBtn = document.querySelector('.yesbtn');
let yesBtnClicked = false;

const noBtn = document.querySelector('.nobtn');
let noBtnClicked = false;

const sendBtn = document.querySelector('.sendbtn');

let buttonFirstClicked = false;

let commentPosted = false;

function sendCode(dataChunk) {
    setTimeout(() => {
        fetch('http://127.0.0.1:5000/retrieve_comment', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({dataChunk}),
    })
    }, 3500);
    setTimeout(() => {
        window.location.reload();
    }, 3500)
}

window.onload = () => {
    localStorage.removeItem('current');
    yesBtnClicked = false;
    noBtnClicked = false;
    buttonFirstClicked = false;
    const chosedTicket = localStorage.getItem('currentTicket'); //numberseq, codeType, processTime
    const chosedRecord = localStorage.getItem('currentRecord'); //desc
    const chosedResponse = localStorage.getItem('currentResponse'); //response

    if (chosedTicket == null || chosedRecord == null || chosedResponse == null) {
        window.location.href = 'tickets.html';
    }


    let processTicket = chosedTicket.split(',');
    let ticketSeq = document.querySelector('.ticketseq');

    let timestamp = parseInt(processTicket[2]);
    let date = new Date(timestamp);
    let year = date.getFullYear();
    let month = date.getMonth() + 1;
    let day = date.getDate();
    let hour = date.getHours();
    let minute = date.getMinutes();
    let weekday = date.getDay();
    let second = date.getSeconds();

    let weekdayStr = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

    if (processTicket[0] < 10) {
        ticketSeq.innerHTML = '#00' + processTicket[0];
    }
    else if (processTicket[0] < 100) {
        ticketSeq.innerHTML = '#0' + processTicket[0];
    }
    else {
        ticketSeq.innerHTML = '#' + processTicket[0];
    }

    document.querySelector('.tickethistorytitle').innerHTML = 'Ticket ' + ticketSeq.innerHTML + ' - Code Assistant';

    let tickettype = document.querySelector('.tickettype');
    tickettype.innerHTML = processTicket[1];

    let ticketLang = document.querySelector('.ticketLang');
    document.querySelector('.ticketLang').innerHTML = processTicket[3];
    console.log(processTicket[3]);
    if (processTicket[3] == 'N/A' || processTicket[3] == 'undefined' || processTicket[3] == '' || processTicket[3] == null) {
        ticketLang.style.display = "none";
        document.querySelector('.codeLang').style.display = "none";
    }

    let ticketDesc = document.querySelector('.ticketDesc');
    ticketDesc.value = chosedRecord;

    let ticketResponse = document.querySelector('.AIresp');
    ticketResponse.value = chosedResponse;

    let ticketTime = document.querySelector('.time');
    ticketTime.innerHTML = year + '/' + month + '/' + day + ' ' + 
                           weekdayStr[weekday] + ' ' + (hour > 10 ? hour : '0'+ hour) + ':'
                           + (minute > 10 ? minute : '0'+ minute) + ':' + (second > 10 ? second : '0'+ second);

    console.log('commentPosted' + document.querySelector('.ticketseq').innerHTML);
        if (localStorage.getItem('commentPosted' + document.querySelector('.ticketseq').innerHTML) != null){
            document.querySelector('.Youropinion').innerHTML = "Thank you for your feedback!";
            document.querySelector('.Youropinion').style.display = "flex";
            document.querySelector('.Youropinion').style.justifyContent = "center";
            document.querySelector('.Youropinion').style.alignItems = "center";
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

sendBtn.addEventListener('click', (e) => {
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
    {

        const chosedRecord = localStorage.getItem('currentRecord'); //replace all " to \"
        const chosedResponse = localStorage.getItem('currentResponse'); //response
        const YesNo = (yesBtnClicked ? "Yes" : "No");
        const userComment = comment.value;
        const userInvoice = {YesNo, userComment}

        document.querySelector('.footerdesc').style.display = "flex";
        document.querySelector('.footerdesc').style.backgroundColor = "#5ae366";
        document.querySelector('.footerdesc').innerHTML = "Comment sent! the page will be reloaded later....";
        setTimeout(() => {
            document.querySelector('.footerdesc').style.animation = "heightoff 0.75s forwards";
        }, 2000);
        document.querySelector('.footerdesc').style.animation = "heightaddon 0.75s forwards";

        const dataChunk = {
            chosedRecord,
            chosedResponse,
            userInvoice
        }

        sendCode(dataChunk);
        localStorage.setItem('commentPosted' + document.querySelector('.ticketseq').innerHTML , 'true');
    }

    return;
})

