document.getElementById('openFlipbookButton').addEventListener('click', function() {
    adjustFlipbookScale();
    document.getElementById('overlay').style.display = 'block';
    document.getElementById('flipbookContainer').style.display = 'block';
    document.body.classList.add('darkened');

    // Reset the flipbook to the first page every time it's opened
    resetFlipbook();
    changePage(1);
});

window.addEventListener('resize', adjustFlipbookScale);

function adjustFlipbookScale() {
    const container = document.getElementById('flipbookContainer');
    const scaleX = window.innerWidth / 1200;  // Base width 1200px
    const scaleY = window.innerHeight / 600;  // Base height 600px
    const scale = Math.min(scaleX, scaleY);  // Keep the aspect ratio consistent
    container.style.transform = `translate(-50%, -50%) scale(${scale})`;
}

document.getElementById('overlay').addEventListener('click', closeFlipbook);

function closeFlipbook() {
    document.getElementById('overlay').style.display = 'none';
    document.getElementById('flipbookContainer').style.display = 'none';
    document.body.classList.remove('darkened');

    // Reset the flipbook state when closed
    resetFlipbook();
}

function resetFlipbook() {
    // Reset currentPage to 1
    currentPage = 1;

    // Remove active and previous classes from all pages
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => {
        page.classList.remove('active');
        page.classList.remove('previous');
    });

    // Ensure the first page is in the active state
    const firstPage = document.getElementById('page1');
    if (firstPage) {
        firstPage.classList.add('active');
    }
}

let currentPage = 1;
const totalPages = document.querySelectorAll('.page').length;

document.getElementById('prevPageButton').addEventListener('click', function() {
    if (currentPage > 1) {
        changePage(currentPage - 1);
    }
});

document.getElementById('nextPageButton').addEventListener('click', function() {
    if (currentPage < totalPages) {
        changePage(currentPage + 1);
    }
});

function changePage(pageNumber) {
    const current = document.getElementById(`page${currentPage}`);
    const next = document.getElementById(`page${pageNumber}`);

    current.classList.remove('active');
    next.classList.add('active');

    if (pageNumber > currentPage) {
        current.classList.add('previous');
    } else {
        next.classList.remove('previous');
    }

    currentPage = pageNumber;
}

// Prevent closing the flipbook when clicking inside the flipbook container
document.getElementById('flipbookContainer').addEventListener('click', function(event) {
    event.stopPropagation();
});