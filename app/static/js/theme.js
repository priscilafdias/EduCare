function setTheme(theme) {
    const body = document.body;
    body.className = body.className
        .replace(/theme-\w+/g, '')
        .trim();
    if (theme !== 'default') {
        body.classList.add('theme-' + theme);
    }
    document.getElementById('btnDefault').className = 'theme-btn' + (theme === 'default' ? ' active' : '');
    document.getElementById('btnPink').className = 'theme-btn pink' + (theme === 'pink' ? ' active' : '');
    document.getElementById('btnBlue').className = 'theme-btn blue' + (theme === 'blue' ? ' active' : '');
    localStorage.setItem('educare-theme', theme);
}

document.addEventListener('DOMContentLoaded', function() {
    const saved = localStorage.getItem('educare-theme');
    if (saved) setTheme(saved);
});