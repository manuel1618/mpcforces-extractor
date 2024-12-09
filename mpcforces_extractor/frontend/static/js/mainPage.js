async function uploadFile(file) {
    const chunkSize = 1024 * 1024; // 1MB
    let offset = 0;

    while (offset < file.size) {
        const chunk = file.slice(offset, offset + chunkSize);
        const formData = new FormData();
        formData.append('file', chunk);
        formData.append('filename', file.name);
        formData.append('offset', offset);
        const response = await safeFetch('api/v1/upload-chunk', {
            method: 'POST',
            body: formData
        });
        if (!response.ok) {
            document.getElementById('progress').innerText = `Error: Failed to upload chunk at offset ${offset}`;
            return;
        }
        document.getElementById('progress').innerText = `Uploaded ${Math.min(offset + chunkSize, file.size)} of ${file.size} bytes`;
        offset += chunkSize;
    }
}

function handleFileSelection(inputId, outputId, upload = false, disconnect = false) {
    const fileInput = document.getElementById(inputId);
    fileInput.addEventListener('change', async (event) => {
        const file = event.target.files[0];
        if (file) {
            document.getElementById(outputId).textContent = file.name;

            if (disconnect) {
                await disconnectDb();
            }

            if (upload) {
                // Upload the file if needed
                await uploadFile(file);
            }
        }
    });
}

handleFileSelection('fem-file', 'fem-path', true);                // Upload only
handleFileSelection('mpcf-file', 'mpcf-path', true);              // Upload only
handleFileSelection('spcf-file', 'spcf-path', true);              // Upload only
handleFileSelection('database-file', 'database-path', true, true); // Disconnect first, then upload


document.getElementById("import-db-button").addEventListener("click", async function (event) {
    const file = document.getElementById('database-file').files[0];
    if (!file) {
        alert("Please select a database file.");
        return;
    }

    const response = await safeFetch('/api/v1/import-db', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            database_filename: file.name,
        }),
    });

    if (!response.ok) {
        document.getElementById('progress').innerText = 'Error: Failed to import database';
        return;
    }
    result = await response.json();
    document.getElementById('progress').innerText = result.message;
    
});


document.getElementById('run-button').addEventListener('click', async function () {
    const femFile = document.getElementById('fem-file').files[0];
    const mpcfFile = document.getElementById('mpcf-file').files[0];
    const spcfFile = document.getElementById('spcf-file').files[0];

    const progressBar = document.querySelector('.progress-bar');
    const progressBarContainer = document.querySelector('.progress');

    // Validate file selection
    if (!femFile) {
        alert("Please select a .fem file.");
        return;
    }
    if (!spcfFile && !mpcfFile) {
        alert("No spcf and mpcf file selected. The extractor will not run.");
        return;
    } else if (!spcfFile) {
        alert("Info: No spcf file selected. The extractor will run without it.");
    } else if (!mpcfFile) {
        alert("Info: No mpcf file selected. The extractor will run without it.");
    }

    let mpcf_filename = mpcfFile ? mpcfFile.name : "";
    let spcf_filename = spcfFile ? spcfFile.name : "";

    // Reset progress bar
    progressBar.style.width = '0%';
    progressBar.setAttribute('aria-valuenow', 0);
    progressBar.innerText = '0%';

    progressBarContainer.style.display = 'block'; // Ensure the bar is visible

    try {
        // Disconnect the database if necessary
        await disconnectDb();

        // Notfy the user that the extractor is running
        document.getElementById('run-button').disabled = true;
        document.getElementById('run-button').innerText = 'Running...';
        progressBar.style.width = '5%';
        progressBar.setAttribute('aria-valuenow', 100);
        progressBar.innerText = '5%';

        // Send request to run the extractor
        const response = await safeFetch('/api/v1/run-extractor', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                fem_filename: femFile.name,
                mpcf_filename: mpcf_filename,
                spcf_filename: spcf_filename,
            }),
        });

        if (!response.ok) {
            progressBar.style.width = '100%';
            progressBar.setAttribute('aria-valuenow', 100);
            progressBar.classList.add('bg-danger');
            progressBar.innerText = 'Error: Failed to run extractor.';
            return;
        }

        // Simulate progress updates (replace with real progress if backend supports it)
        await simulateProgress(progressBar);

        // Handle successful response
        const result = await response.json();
        progressBar.classList.remove('bg-danger');
        progressBar.classList.add('bg-success');
        progressBar.innerText = `Completed: ${result.message}`;
        progressBar.style.width = '100%';
        progressBar.setAttribute('aria-valuenow', 100);
        document.getElementById('run-button').disabled = false;
        document.getElementById('run-button').innerText = 'Run Extractor';
    } catch (error) {
        progressBar.style.width = '100%';
        progressBar.setAttribute('aria-valuenow', 100);
        progressBar.classList.add('bg-danger');
        progressBar.innerText = `Error: ${error.message}`;
        document.getElementById('run-button').disabled = false;
        document.getElementById('run-button').innerText = 'Run Extractor';
    }
});

/**
 * Simulates progress updates for a more dynamic experience.
 * Replace this with real progress streaming if backend supports it.
 */
async function simulateProgress(progressBar) {
    const steps = 8; // Number of simulated progress steps
    for (let i = 1; i <= steps; i++) {
        const timeout = Math.random() * 500; // Random delay up to 0.5s
        await new Promise(resolve => setTimeout(resolve, timeout)); // Simulate delay
        const progress = (i / steps) * 100;
        progressBar.style.width = `${progress}%`;
        progressBar.setAttribute('aria-valuenow', Math.round(progress));
        progressBar.innerText = `${Math.round(progress)}%`;
    }
}


// Call the function to fetch the directory when the page loads
window.addEventListener('DOMContentLoaded', async function () {
    const response = await safeFetch('/api/v1/get-output-folder');
    if (!response.ok) {
        document.getElementById('directory-hint').innerText = 'Error fetching directory.';
        return;
    }
    const result = await response.json()
    document.getElementById('directory-hint').innerText = `Hint: ${result.output_folder}`;
});

document.getElementById('main-title').addEventListener('click', function() {
    location.reload(); // Reload the page
});