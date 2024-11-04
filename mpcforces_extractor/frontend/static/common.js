document.addEventListener('DOMContentLoaded', function() {
    const toggleButton = document.getElementById('dark-mode-toggle');
    const body = document.body;

    const darkMode = localStorage.getItem('dark-mode');
    if (darkMode === 'enabled') {
        body.classList.add('dark-mode');
        toggleButton.textContent = 'Light Mode';
    } else {
        body.classList.remove('dark-mode');
        body.classList.add('light-mode');
        toggleButton.textContent = 'Dark Mode';
    }

    toggleButton.addEventListener('click', function() {
        if (body.classList.contains('dark-mode')) {
            body.classList.remove('dark-mode');
            localStorage.setItem('dark-mode', 'disabled');
            toggleButton.textContent = 'Dark Mode';
        } else {
            body.classList.add('dark-mode');
            localStorage.setItem('dark-mode', 'enabled');
            toggleButton.textContent = 'Light Mode';
        }
    });

  

});


function createCopyButton(textToCopy, buttonText = 'Copy', copiedText = 'Copied!') {
    const button = document.createElement('button');
    button.className = 'btn btn-secondary btn-sm';
    button.textContent = buttonText;

    button.addEventListener('click', () => {
        navigator.clipboard.writeText(textToCopy).then(() => {
            const originalText = button.textContent;
            button.textContent = copiedText;
            button.style.backgroundColor = '#4CAF50';
            button.style.color = '#fff';

            setTimeout(() => {
                button.textContent = originalText;
                button.style.backgroundColor = '';
                button.style.color = '';
            }, 1500);
        }).catch(err => {
            console.error('Failed to copy text:', err);
        });
    });

    return button;
}