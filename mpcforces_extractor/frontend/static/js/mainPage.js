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

    disconnectDb();
    
    const response = await safeFetch('/api/v1/run-extractor', {
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
        document.getElementById('progress').innerText = 'Error: Failed to run extractor';
        return;
    }
    
    result = await response.json();
    document.getElementById('progress').innerText = result.message;

});

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