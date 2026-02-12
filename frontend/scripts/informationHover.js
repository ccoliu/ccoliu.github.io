document.getElementById('openFlipbookButton').addEventListener('click', function () {
    const flipbookContainer = document.getElementById('flipbookContainer');

    // Create a new div to display the image
    const pushImage = document.createElement('div');
    pushImage.classList.add('pushImageEffect');

    // Insert the image next to the flipbookContainer
    flipbookContainer.parentNode.insertBefore(pushImage, flipbookContainer.nextSibling);

    // Remove the image element after the fade-out animation ends
    pushImage.addEventListener('animationend', function () {
        pushImage.remove();
    });

    // Show and adjust the flipbook
    adjustFlipbookScale();
    document.getElementById('overlay').style.display = 'block';
    flipbookContainer.style.display = 'block';
    document.body.classList.add('darkened');

    // Reset the flipbook and set it to the first page
    resetFlipbook();
    changePage(1);
});

window.addEventListener('resize', adjustFlipbookScale);

function adjustFlipbookScale() {
    const container = document.getElementById('flipbookContainer');
    const scaleX = window.innerWidth / 1200; // Base width 1200px
    const scaleY = window.innerHeight / 600; // Base height 600px
    const scale = Math.min(scaleX, scaleY); // Keep the aspect ratio consistent
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
    pages.forEach((page) => {
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

document.getElementById('prevPageButton').addEventListener('click', function () {
    if (currentPage > 1) {
        changePage(currentPage - 1);
    }
});

document.getElementById('nextPageButton').addEventListener('click', function () {
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
document.getElementById('flipbookContainer').addEventListener('click', function (event) {
    event.stopPropagation();
});

// Tooltip display function
function showTooltip() {
    const tooltipText = document.querySelector('.tooltipText');
    if (!tooltipText) return;

    tooltipText.innerHTML = ''; // Clear original content
    const text = 'Need Help ?';

    text.split('').forEach((letter, index) => {
        const span = document.createElement('span');
        span.textContent = letter === ' ' ? '\u00A0' : letter; // Replace space with non-breaking space
        span.style.animation = `flyIn 0.5s ease forwards ${index * 0.04}s`; // Set animation for each letter to appear gradually
        tooltipText.appendChild(span);
    });

    tooltipText.style.opacity = 1; // Ensure the tooltip is visible
    tooltipText.style.visibility = 'visible';
}

// Tooltip hide function
function hideTooltip() {
    const tooltipText = document.querySelector('.tooltipText');
    if (!tooltipText) return;

    tooltipText.style.opacity = 0; // Hide the tooltip
    tooltipText.style.visibility = 'hidden';
    tooltipText.innerHTML = ''; // Clear the text
}

// Mouse hover for "Need Help?" effect
document.getElementById('openFlipbookButton').addEventListener('mouseover', function () {
    hideIdleTooltip(); // Hide the idle tooltip if visible
    showTooltip();
});

document.getElementById('openFlipbookButton').addEventListener('mouseout', function () {
    hideTooltip();
    startIdleTimer(); // Reset idle timer when mouse leaves the button
});

// Idle detection for showing tooltip after inactivity
let idleTimer;
let idleTooltipVisible = false; // To track if the idle tooltip is currently visible

function startIdleTimer() {
    clearTimeout(idleTimer); // Reset timer whenever there's activity
    idleTimer = setTimeout(showIdleTooltip, 5000); // Set the timer to show the idle tooltip after 5 seconds
}

function showIdleTooltip() {
    if (!idleTooltipVisible) {
        showTooltip();
        idleTooltipVisible = true;
    }
}

function hideIdleTooltip() {
    if (idleTooltipVisible) {
        hideTooltip();
        idleTooltipVisible = false;
    }
}

// Register events to detect user activity
['mousemove', 'keydown', 'scroll', 'click'].forEach((event) => {
    window.addEventListener(event, () => {
        hideIdleTooltip(); // Hide idle tooltip if user interacts
        startIdleTimer(); // Reset idle timer
    });
});

// Start the idle timer when the page loads
startIdleTimer();
