const circle = document.getElementById('profileCircle');
let isDragging = false;
let hasMoved = false;
let startX, startY;

function loadPosition() {
    const pos = localStorage.getItem('profileCirclePos');
    if (pos) {
        const { x, y } = JSON.parse(pos);
        circle.style.left = x + 'px';
        circle.style.top = y + 'px';
        circle.style.right = 'auto';
        circle.style.bottom = 'auto';
    }
}

function savePosition(x, y) {
    localStorage.setItem('profileCirclePos', JSON.stringify({ x, y }));
}

function initPosition() {
    const hasSaved = localStorage.getItem('profileCirclePos');
    if (!hasSaved) {
        circle.style.bottom = '30px';
        circle.style.right = '30px';
        circle.style.top = 'auto';
        circle.style.left = 'auto';
    } else {
        loadPosition();
    }
}

circle.addEventListener('mousedown', function(e) {
    isDragging = true;
    hasMoved = false;
    const rect = circle.getBoundingClientRect();
    startX = e.clientX - rect.left;
    startY = e.clientY - rect.top;
    circle.style.cursor = 'grabbing';
    e.preventDefault();
});

document.addEventListener('mousemove', function(e) {
    if (!isDragging) return;
    hasMoved = true;
    let newX = e.clientX - startX;
    let newY = e.clientY - startY;
    const circleSize = circle.offsetWidth || 60;
    newX = Math.max(0, Math.min(window.innerWidth - circleSize, newX));
    newY = Math.max(0, Math.min(window.innerHeight - circleSize, newY));
    circle.style.left = newX + 'px';
    circle.style.top = newY + 'px';
    circle.style.right = 'auto';
    circle.style.bottom = 'auto';
});

document.addEventListener('mouseup', function(e) {
    if (isDragging && hasMoved) {
        const rect = circle.getBoundingClientRect();
        savePosition(rect.left, rect.top);
    }
    if (isDragging) {
        isDragging = false;
        circle.style.cursor = 'grab';
        if (!hasMoved) { openProfile(); }
        hasMoved = false;
    }
});

circle.addEventListener('touchstart', function(e) {
    const touch = e.touches[0];
    isDragging = true;
    hasMoved = false;
    const rect = circle.getBoundingClientRect();
    startX = touch.clientX - rect.left;
    startY = touch.clientY - rect.top;
}, { passive: true });

document.addEventListener('touchmove', function(e) {
    if (!isDragging) return;
    const touch = e.touches[0];
    hasMoved = true;
    let newX = touch.clientX - startX;
    let newY = touch.clientY - startY;
    const circleSize = circle.offsetWidth || 60;
    newX = Math.max(0, Math.min(window.innerWidth - circleSize, newX));
    newY = Math.max(0, Math.min(window.innerHeight - circleSize, newY));
    circle.style.left = newX + 'px';
    circle.style.top = newY + 'px';
    circle.style.right = 'auto';
    circle.style.bottom = 'auto';
}, { passive: true });

document.addEventListener('touchend', function(e) {
    if (isDragging) {
        if (hasMoved) {
            const rect = circle.getBoundingClientRect();
            savePosition(rect.left, rect.top);
        } else {
            openProfile();
        }
        isDragging = false;
        hasMoved = false;
    }
}, { passive: true });

circle.addEventListener('click', function(e) {
    if (!hasMoved) { openProfile(); }
});

window.addEventListener('load', function() {
    setTimeout(initPosition, 100);
});

window.addEventListener('resize', function() {
    const rect = circle.getBoundingClientRect();
    const circleSize = circle.offsetWidth || 60;
    let newX = Math.min(rect.left, window.innerWidth - circleSize);
    let newY = Math.min(rect.top, window.innerHeight - circleSize);
    newX = Math.max(0, newX);
    newY = Math.max(0, newY);
    if (rect.left !== newX || rect.top !== newY) {
        circle.style.left = newX + 'px';
        circle.style.top = newY + 'px';
        savePosition(newX, newY);
    }
});

document.addEventListener('keydown', function(e) {
    if (e.altKey && e.key === 'p') {
        e.preventDefault();
        openProfile();
    }
});
