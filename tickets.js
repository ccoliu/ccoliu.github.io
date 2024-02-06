function uploadTicket() {
    let numberseq = localStorage.getItem('numberseq');
    console.log('numberseq: ' + numberseq);
    let numberseqInt = numberseq - 1;
    for (let i = 1; i <= 10; i++)
    {
        if (numberseqInt >= 0)
        {
            let ticket = localStorage.getItem('ticket' + "\"" + numberseqInt + "\"");
            console.log('ticket' + "\"" + numberseqInt + "\"");
            let ticketTitle = document.querySelector('.ticket' + i + ' .ticketTitle');
            let ticketSeq = document.querySelector('.ticket' + i + ' .ticketseq');
            console.log(ticket);
            console.log(ticket[0]);
            ticketTitle.innerHTML = ticket[codeType];
            ticketSeq.innerHTML = '#' + ticket[0];
            numberseqInt--;
        }
        else
        {
            continue;
        }
    }
}

window.addEventListener('load', function() {
    console.log('ticket.js loaded');
    uploadTicket();
})
