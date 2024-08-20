let currentProgress = 0;
let targetProgress = 0;

function updateProgress(newPercentage) {
    targetProgress = newPercentage;
    const progressBar = document.getElementById('progress-bar');
    const progressContainer = document.getElementById("progress-container");

    // 如果新进度小于当前进度，意味着需要回退
    if (targetProgress < currentProgress) {
        // 使用回退动画
        progressBar.style.transition = 'width 1s ease';
        progressBar.style.width = targetProgress + '%';
        // Hide the progress bar after the animation ends in 3 seconds
        setTimeout(() => {
            progressContainer.classList.remove('show');
        }, 1000);
    } else {
        // 增长动画
        progressBar.style.transition = 'width 1s ease';
        progressBar.style.width = targetProgress + '%';
    }

    // 更新当前进度
    currentProgress = targetProgress;
}