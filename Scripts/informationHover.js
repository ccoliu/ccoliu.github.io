document.getElementById('openFlipbookButton').addEventListener('click', function() {
    document.getElementById('overlay').style.display = 'block';
    document.getElementById('flipbookContainer').style.display = 'block';
    document.body.classList.add('darkened');
    changePage(1);
});

// 点击overlay或非悬浮窗口区域关闭flipbook
document.getElementById('overlay').addEventListener('click', closeFlipbook);

function closeFlipbook() {
    document.getElementById('overlay').style.display = 'none';
    document.getElementById('flipbookContainer').style.display = 'none';
    document.body.classList.remove('darkened');
    
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

// 阻止点击flipbookContainer时关闭窗口
document.getElementById('flipbookContainer').addEventListener('click', function(event) {
    event.stopPropagation();
});