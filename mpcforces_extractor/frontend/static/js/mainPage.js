async function uploadFile(file) {
    const chunkSize = 1024 * 1024; // 1MB
    let offset = 0;

    while (offset < file.size) {
        const chunk = file.slice(offset, offset + chunkSize);
        const formData = new FormData();
        formData.append('file', chunk);
        formData.append('filename', file.name);
        formData.append('offset', offset);

        const response = await fetch('api/v1/upload-chunk', {
            method: 'POST',
            body: formData
        });

        
        document.getElementById('progress').innerText = `Uploaded ${Math.min(offset + chunkSize, file.size)} of ${file.size} bytes`;

        offset += chunkSize;
    }
}


// Dark mode toggle functionality
document.getElementById('dark-mode-toggle').addEventListener('click', function () {
    const currentTheme = document.documentElement.classList.toggle('dark-mode') ? 'dark' : 'light';
    localStorage.setItem('theme', currentTheme);
});

// File input change event handlers
document.getElementById('fem-file').addEventListener('change', function (event) {
    const file = event.target.files[0];
    document.getElementById('fem-path').textContent = file.name;
    uploadFile(file);  // Call the function from mainPage.js
});

document.getElementById('mpcf-file').addEventListener('change', function (event) {
    const file = event.target.files[0];
    document.getElementById('mpcf-path').textContent = file.name;
    uploadFile(file);  // Call the function from mainPage.js
});


// Fetch directory path on page load
async function fetchDefaultDir() {
    try {
        const response = await fetch('/api/v1/get-output-folder');
        if (!response.ok) throw new Error('Failed to fetch directory path');
        const result = await response.json();

        // Display the directory path as a reference for the user
        document.getElementById('directory-hint').innerText = `Hint: ${result.output_folder}`;
    } catch (error) {
        console.error('Error fetching directory:', error);
    }
}

// Call the function to fetch the directory when the page loads
window.addEventListener('DOMContentLoaded', fetchDefaultDir);

// Db File input / output event handlers
document.getElementById('database-file').addEventListener('change', function (event) {
    const file = event.target.files[0];
    document.getElementById('database-path').textContent = file.name;
    const rsp = fetch('/api/v1/disconnect-db', {
        method: 'POST',
        body: file,
        timeout: 500,
    });
    if (!rsp.ok) {
        console.error('Failed to disconnect from database');
    }

    uploadFile(file);  // Call the function from mainPage.js
});

document.getElementById("import-db-button").addEventListener("click", async function (event) {
    const file = document.getElementById('database-file').files[0];
    if (!file) {
        alert("Please select a database file.");
        return;
    }

    const response = await fetch('/api/v1/import-db', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            database_filename: file.name,
        }),
    });

    if (!response.ok) {
        const error = await response.text();
        document.getElementById('progress').innerText = `Error: ${error}`;
    } else {
        const result = await response.json();
        document.getElementById('progress').innerText = `Success: ${result.message}`;
    }
});


// Run Button Click Event Handler
document.getElementById('run-button').addEventListener('click', async function () {
    const femFile = document.getElementById('fem-file').files[0];
    const mpcfFile = document.getElementById('mpcf-file').files[0];

    if (!femFile) {
        alert("Please select both .fem file.");
        return;
    }

    let mpcf_filename = ""
    if (mpcfFile) {
        mpcf_filename = mpcfFile.name
    }

    // disconnect the database
    const rsp = fetch('/api/v1/disconnect-db', {
        method: 'POST',
        timeout: 500,
    });
    if (!rsp.ok) {
        console.error('Failed to disconnect from database');
    }

    const response = await fetch('/api/v1/run-extractor', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            fem_filename: femFile.name,
            mpcf_filename: mpcf_filename,
        }),
    });

    if (!response.ok) {
        const error = await response.text();
        document.getElementById('progress').innerText = `Error: ${error}`;
    } else {
        const result = await response.json();
        document.getElementById('progress').innerText = `Success: ${result.message}`;
    }
});

