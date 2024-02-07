
function uploadTicket() {
    let avaliableTicket = 0;
    let numberseq = localStorage.getItem('numberseq');
    console.log('numberseq: ' + numberseq);
    let numberseqInt = numberseq - 1;
    for (let i = 1; i <= 10; i++)
    {
        if (numberseqInt > 0)
        {
            avaliableTicket++;

            let ticket = localStorage.getItem('ticket' + numberseqInt); //numberseq, codeType, processTime
            let record = localStorage.getItem('record' + numberseqInt); //response
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

            ticketTime.innerHTML = year % 2000 + '/' + month + '/' + day + ' ' + weekdayStr[weekday] + ' ' + (hour > 10 ? hour : '0'+ hour) + ':' + (minute > 10 ? minute : '0'+ minute);
            
            numberseqInt--;
        }
        else
        {
            let ticket = document.querySelector('.ticket' + i);
            ticket.style.visibility = 'hidden';
        }
    }
    return avaliableTicket;
}

window.addEventListener('load', function() {
    console.log('ticket.js loaded');
    let Tickets = uploadTicket();
    document.querySelector('.TicketInfo').innerHTML = "Available Tickets: " + Tickets;
});