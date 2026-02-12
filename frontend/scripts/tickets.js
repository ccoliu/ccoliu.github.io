
let associatedTicketSeq = new Array(11);
let numberseq = localStorage.getItem('numberseq') - 1;
let currentPage = 1;
let totalPage = Math.floor(numberseq / 10) + (numberseq % 10 > 0 ? 1 : 0);

function uploadTicketloop(numberseqInt) {
    for (let i = 1; i <= 10; i++)
        {
            if (numberseqInt > 0)
            {
                let ticketButton = document.querySelector('.ticket' + i);
                ticketButton.style.display = 'block';

                associatedTicketSeq[i] = numberseqInt;
    
                let ticket = localStorage.getItem('ticket' + numberseqInt); //numberseq, codeType, processTime
                let record = localStorage.getItem('record' + numberseqInt); //response
                let id = localStorage.getItem('id' + numberseqInt);
                console.log('ticket' + numberseqInt);
                let ticketAttr = ticket.split(',');
    
                let ticketTitle = document.querySelector('.ticket' + i + ' .ticketTitle');
                let ticketSeq = document.querySelector('.ticket' + i + ' .ticketseq');
                let ticketDesc = document.querySelector('.ticket' + i + ' .ticketDescription');
                let ticketTime = document.querySelector('.ticket' + i + ' .ticketCreateTime');
    
                let timestamp = parseInt(ticketAttr[2]);
                let date = new Date(timestamp);
                let year = date.getFullYear();
                let month = date.getMonth() + 1;
                let day = date.getDate();
                let hour = date.getHours();
                let minute = date.getMinutes();
                let weekday = date.getDay();
    
                let weekdayStr = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
                
                console.log(id);
                console.log(ticket);
                console.log(ticket[0]);
                console.log(ticketAttr[0]);
                console.log(ticketAttr[1]);
                console.log(ticketAttr[2]);
                
                let ticketnum = parseInt(ticketAttr[0]);
                if (ticketnum < 10)
                {
                    ticketSeq.innerHTML = "#00" + ticketnum;
                }
                else if (ticketnum < 100)
                {
                    ticketSeq.innerHTML = "#0" + ticketnum;
                }
                else
                {
                    ticketSeq.innerHTML = "#" + ticketnum;
                }
                
                if (record.length > 250)
                {
                    ticketDesc.innerHTML = record.substring(0, 250) + '...';
                }
                else
                {
                    ticketDesc.innerHTML = record;
                }
    
                ticketTitle.innerHTML = ticketAttr[1];
    
                ticketTime.innerHTML = year % 2000 + '/' + month + '/' + day + ' ' + weekdayStr[weekday] + ' ' + (hour >= 10 ? hour : '0' + hour) + ':' + (minute >= 10 ? minute : '0' + minute);
                
                numberseqInt--;
            }
            else
            {
                let ticket = document.querySelector('.ticket' + i);
                ticket.style.display = 'none';
            }
        }
}

function uploadTicket() {
    const PageInfo = document.querySelector('.pageInfo');

    console.log('numberseq: ' + numberseq);
    let numberseqInt = numberseq;

    PageInfo.innerHTML =  currentPage + " / " + totalPage;

    uploadTicketloop(numberseqInt);
}



window.addEventListener('load', function() {
    console.log('ticket.js loaded');
    uploadTicket();
    document.querySelector('.TicketInfo').innerHTML = "Available Tickets: " + numberseq;
});

const prevPage = document.querySelector('.prevPage');
const nextPage = document.querySelector('.nextPage');

prevPage.addEventListener('click', () => {
    if (currentPage > 1)
    {
        currentPage--;
        let numberseqInt = numberseq - ((currentPage - 1) * 10);
        console.log(numberseqInt);
        uploadTicketloop(numberseqInt);

        const PageInfo = document.querySelector('.pageInfo');
        PageInfo.innerHTML =  currentPage + " / " + totalPage;
        window.scrollTo(0, 0);
    }
});

nextPage.addEventListener('click', () => {
    if (currentPage < totalPage)
    {
        currentPage++;
        let numberseqInt = numberseq - ((currentPage - 1) * 10);
        console.log(numberseqInt);
        uploadTicketloop(numberseqInt);

        const PageInfo = document.querySelector('.pageInfo');
        PageInfo.innerHTML =  currentPage + " / " + totalPage;
        window.scrollTo(0, 0);
    }
});

let ticket1 = document.querySelector('.ticket1');
let ticket2 = document.querySelector('.ticket2');
let ticket3 = document.querySelector('.ticket3');
let ticket4 = document.querySelector('.ticket4');
let ticket5 = document.querySelector('.ticket5');
let ticket6 = document.querySelector('.ticket6');
let ticket7 = document.querySelector('.ticket7');
let ticket8 = document.querySelector('.ticket8');
let ticket9 = document.querySelector('.ticket9');
let ticket10 = document.querySelector('.ticket10');

ticket1.addEventListener('click', () => {
    chosedticket = localStorage.getItem('ticket' + associatedTicketSeq[1]); //numberseq, codeType, processTime
    chosedrecord = localStorage.getItem('record' + associatedTicketSeq[1]); //record
    chosedresponse = localStorage.getItem('response' + associatedTicketSeq[1]); //response
    chosedID = localStorage.getItem('id' + associatedTicketSeq[1]); //response
    localStorage.setItem('currentTicket', chosedticket);
    localStorage.setItem('currentRecord', chosedrecord);
    localStorage.setItem('currentResponse', chosedresponse);
    localStorage.setItem('currentID', chosedID);
    window.location.href = 'tickethistory.html';
});

ticket2.addEventListener('click', () => {
    chosedticket = localStorage.getItem('ticket' + associatedTicketSeq[2]); //numberseq, codeType, processTime
    chosedrecord = localStorage.getItem('record' + associatedTicketSeq[2]); //response
    chosedresponse = localStorage.getItem('response' + associatedTicketSeq[2]); //response
    chosedID = localStorage.getItem('id' + associatedTicketSeq[2]); //response
    localStorage.setItem('currentTicket', chosedticket);
    localStorage.setItem('currentRecord', chosedrecord);
    localStorage.setItem('currentResponse', chosedresponse);
    localStorage.setItem('currentID', chosedID);
    window.location.href = 'tickethistory.html';
});

ticket3.addEventListener('click', () => {
    chosedticket = localStorage.getItem('ticket' + associatedTicketSeq[3]); //numberseq, codeType, processTime
    chosedrecord = localStorage.getItem('record' + associatedTicketSeq[3]); //response
    chosedresponse = localStorage.getItem('response' + associatedTicketSeq[3]); //response
    chosedID = localStorage.getItem('id' + associatedTicketSeq[3]); //response
    localStorage.setItem('currentTicket', chosedticket);
    localStorage.setItem('currentRecord', chosedrecord);
    localStorage.setItem('currentResponse', chosedresponse);
    localStorage.setItem('currentID', chosedID);
    window.location.href = 'tickethistory.html';
});

ticket4.addEventListener('click', () => {
    chosedticket = localStorage.getItem('ticket' + associatedTicketSeq[4]); //numberseq, codeType, processTime
    chosedrecord = localStorage.getItem('record' + associatedTicketSeq[4]); //response
    chosedresponse = localStorage.getItem('response' + associatedTicketSeq[4]); //response
    chosedID = localStorage.getItem('id' + associatedTicketSeq[4]); //response
    localStorage.setItem('currentTicket', chosedticket);
    localStorage.setItem('currentRecord', chosedrecord);
    localStorage.setItem('currentResponse', chosedresponse);
    localStorage.setItem('currentID', chosedID);
    window.location.href = 'tickethistory.html';
});

ticket5.addEventListener('click', () => {
    chosedticket = localStorage.getItem('ticket' + associatedTicketSeq[5]); //numberseq, codeType, processTime
    chosedrecord = localStorage.getItem('record' + associatedTicketSeq[5]); //response
    chosedresponse = localStorage.getItem('response' + associatedTicketSeq[5]); //response
    chosedID = localStorage.getItem('id' + associatedTicketSeq[5]); //response
    localStorage.setItem('currentTicket', chosedticket);
    localStorage.setItem('currentRecord', chosedrecord);
    localStorage.setItem('currentResponse', chosedresponse);
    localStorage.setItem('currentID', chosedID);
    window.location.href = 'tickethistory.html';
});

ticket6.addEventListener('click', () => {
    chosedticket = localStorage.getItem('ticket' + associatedTicketSeq[6]); //numberseq, codeType, processTime
    chosedrecord = localStorage.getItem('record' + associatedTicketSeq[6]); //response
    chosedresponse = localStorage.getItem('response' + associatedTicketSeq[6]); //response
    chosedID = localStorage.getItem('id' + associatedTicketSeq[6]); //response
    localStorage.setItem('currentTicket', chosedticket);
    localStorage.setItem('currentRecord', chosedrecord);
    localStorage.setItem('currentResponse', chosedresponse);
    localStorage.setItem('currentID', chosedID);
    window.location.href = 'tickethistory.html';
});

ticket7.addEventListener('click', () => {
    chosedticket = localStorage.getItem('ticket' + associatedTicketSeq[7]); //numberseq, codeType, processTime
    chosedrecord = localStorage.getItem('record' + associatedTicketSeq[7]); //response
    chosedresponse = localStorage.getItem('response' + associatedTicketSeq[7]); //response
    chosedID = localStorage.getItem('id' + associatedTicketSeq[7]); //response
    localStorage.setItem('currentTicket', chosedticket);
    localStorage.setItem('currentRecord', chosedrecord);
    localStorage.setItem('currentResponse', chosedresponse);
    localStorage.setItem('currentID', chosedID);
    window.location.href = 'tickethistory.html';
});

ticket8.addEventListener('click', () => {
    chosedticket = localStorage.getItem('ticket' + associatedTicketSeq[8]); //numberseq, codeType, processTime
    chosedrecord = localStorage.getItem('record' + associatedTicketSeq[8]); //response
    chosedresponse = localStorage.getItem('response' + associatedTicketSeq[8]); //response
    chosedID = localStorage.getItem('id' + associatedTicketSeq[8]); //response
    localStorage.setItem('currentTicket', chosedticket);
    localStorage.setItem('currentRecord', chosedrecord);
    localStorage.setItem('currentResponse', chosedresponse);
    localStorage.setItem('currentID', chosedID);
    window.location.href = 'tickethistory.html';
});

ticket9.addEventListener('click', () => {
    chosedticket = localStorage.getItem('ticket' + associatedTicketSeq[9]); //numberseq, codeType, processTime
    chosedrecord = localStorage.getItem('record' + associatedTicketSeq[9]); //response
    chosedresponse = localStorage.getItem('response' + associatedTicketSeq[9]); //response
    chosedID = localStorage.getItem('id' + associatedTicketSeq[9]); //response
    localStorage.setItem('currentTicket', chosedticket);
    localStorage.setItem('currentRecord', chosedrecord);
    localStorage.setItem('currentResponse', chosedresponse);
    localStorage.setItem('currentID', chosedID);
    window.location.href = 'tickethistory.html';
});

ticket10.addEventListener('click', () => {
    chosedticket = localStorage.getItem('ticket' + associatedTicketSeq[10]); //numberseq, codeType, processTime
    chosedrecord = localStorage.getItem('record' + associatedTicketSeq[10]); //response
    chosedresponse = localStorage.getItem('response' + associatedTicketSeq[10]); //response
    chosedID = localStorage.getItem('id' + associatedTicketSeq[10]); //response
    localStorage.setItem('currentTicket', chosedticket);
    localStorage.setItem('currentRecord', chosedrecord);
    localStorage.setItem('currentResponse', chosedresponse);
    localStorage.setItem('currentID', chosedID);
    window.location.href = 'tickethistory.html';
});