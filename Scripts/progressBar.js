let currentProgress = 0;
let targetProgress = 0;

function updateProgress(newPercentage) {
    targetProgress = newPercentage;
    const progressBar = document.getElementById('progress-bar');
    
    // 添加一个临时的动画结束监听器，确保光影动画结束后才推进进度条
    progressBar.addEventListener('animationiteration', function() {
        if (currentProgress < targetProgress) {
            progressBar.style.width = targetProgress + '%';
            currentProgress = targetProgress;
        }
    }, { once: true });
}