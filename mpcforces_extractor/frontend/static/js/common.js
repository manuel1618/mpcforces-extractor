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

async function disconnectDb() {
    // Handle database disconnect before upload
    try {
        const response = await fetch('/api/v1/disconnect-db', {
            method: 'POST',
            timeout: 500,
        });
        if (!response.ok) {
            throw new Error('Failed to disconnect from database');
        }
    } catch (error) {
        console.error('Error:', error.message);
        alert('An error occurred while disconnecting from the database.');
        return; // Stop further processing if disconnect fails
    }
}

async function safeFetch(url, options = {}, custom_error_message = null) {
    try {
        const response = await fetch(url, options);
        if (!response.ok) throw new Error(`${response.status}: ${response.statusText}`);
        return response;
    } catch (error) {
        console.log(`Error fetching ${url} using ${options.method}: ${error}`);
        if (custom_error_message) {
            console.log(custom_error_message);
        }
        return null;
    }
}

function displayError(message) {
    let errorContainer = document.getElementById('error-container');
    if (!errorContainer) {
        errorContainer = document.createElement('div');
        errorContainer.id = 'error-container';
        errorContainer.style.color = 'red';
        document.body.prepend(errorContainer);
    }
    errorContainer.textContent = message;
    errorContainer.style.display = 'block';
}

function calculateForceMagnitude(forces) {
    const linear = Math.sqrt(forces[0]**2 + forces[1]**2 + forces[2]**2).toFixed(3);
    const moment = Math.sqrt(forces[3]**2 + forces[4]**2 + forces[5]**2).toFixed(3);
    return { linear, moment };
}

async function fetchSubcases(forceRefresh = false) {
    if (!forceRefresh && cachedSubcases) return cachedSubcases; // Use cached data unless forced
    const response = await safeFetch('/api/v1/subcases');
    if (!response.ok) {
        displayError('Error fetching Subcases.');
        return [];
    }
    cachedSubcases = await response.json();
    populateSubcaseDropdown(cachedSubcases);
    return cachedSubcases;
}

function populateSubcaseDropdown(subcases) {
    subcaseDropdown.innerHTML = '';
    subcases.forEach(subcase => {
        const option = document.createElement('option');
        option.value = subcase.id;
        option.textContent = subcase.id;
        subcaseDropdown.appendChild(option);
    });
}

function parseFilterData(inputElement) {
    return inputElement
        .trim()
        .split(",")
        .map(a => a.trim())
        .filter(a => a !== "");
}