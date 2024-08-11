document.getElementById('openFlipbookButton').addEventListener('click', function() {
    const flipbookContainer = document.getElementById('flipbookContainer');
    
    // 创建一个新的div来显示图片
    const pushImage = document.createElement('div');
    pushImage.classList.add('pushImageEffect');
    
    // 将图片插入到 flipbookContainer 旁边
    flipbookContainer.parentNode.insertBefore(pushImage, flipbookContainer.nextSibling);

    // 当图片淡出动画结束后，移除该图片元素
    pushImage.addEventListener('animationend', function() {
        pushImage.remove();
    });

    // 显示和调整flipbook
    adjustFlipbookScale();
    document.getElementById('overlay').style.display = 'block';
    flipbookContainer.style.display = 'block';
    document.body.classList.add('darkened');

    // 重置翻页并设置到第一页
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

document.getElementById('openFlipbookButton').addEventListener('mouseover', function() {
    const tooltipText = document.querySelector('.tooltipText');
    tooltipText.innerHTML = ''; // 清空原始内容
    const text = "Need Help ?";

    text.split('').forEach((letter, index) => {
        const span = document.createElement('span');
        span.textContent = letter === ' ' ? '\u00A0' : letter;  // 使用不间断空格替换空格
        span.style.animation = `flyIn 0.5s ease forwards ${index * 0.04}s`; // 设置动画，逐字出现
        tooltipText.appendChild(span);
    });

    tooltipText.style.opacity = 1; // 确保tooltip可见
});

document.getElementById('openFlipbookButton').addEventListener('mouseout', function() {
    const tooltipText = document.querySelector('.tooltipText');
    tooltipText.style.opacity = 0; // 隐藏tooltip
    tooltipText.innerHTML = ''; // 清空文字
});