function uploadTicket() {
    let numberseq = localStorage.getItem('numberseq');
    console.log('numberseq: ' + numberseq);
}

window.addEventListener('load', function() {
    console.log('ticket.js loaded');
    uploadTicket();
})
