const yesBtn = document.querySelector('.yesbtn');
let yesBtnClicked = false;

const noBtn = document.querySelector('.nobtn');
let noBtnClicked = false;

let buttonFirstClicked = false;

window.onload = () => {
    yesBtnClicked = false;
    noBtnClicked = false;
    buttonFirstClicked = false;
    const chosedTicket = localStorage.getItem('currentTicket'); //numberseq, codeType, processTime
    const chosedRecord = localStorage.getItem('currentRecord'); //desc
    const chosedResponse = localStorage.getItem('currentResponse'); //response

    if (chosedTicket == null || chosedRecord == null) {
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

    let tickettype = document.querySelector('.tickettype');
    tickettype.innerHTML = processTicket[1];

    let ticketDesc = document.querySelector('.ticketDesc');
    ticketDesc.value = chosedRecord;

    let ticketResponse = document.querySelector('.AIresp');
    ticketResponse.value = chosedResponse;

    let ticketTime = document.querySelector('.time');
    ticketTime.innerHTML = year + '/' + month + '/' + day + ' ' + 
                           weekdayStr[weekday] + ' ' + (hour > 10 ? hour : '0'+ hour) + ':'
                           + (minute > 10 ? minute : '0'+ minute) + ':' + (second > 10 ? second : '0'+ second);
}

function ButtonReturn(button) {
    button.style.backgroundColor = "transparent";
    button.style.border = "1px solid #D0D0D0";
}

yesBtn.addEventListener('click', () => {
    if (buttonFirstClicked == false) {
        document.querySelector('.comment').style.display = "block";
        document.querySelector('.sendbtncontent').style.display = "flex";
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
