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

//Listeners 

// Run button functionality
document.getElementById('run-button').addEventListener('click', async function () {
    console.log('Run button clicked');
    const femFile = document.getElementById('fem-file').files[0];
    const mpcfFile = document.getElementById('mpcf-file').files[0];

    if (!femFile || !mpcfFile) {
        alert("Please select both .fem and .mpcf files.");
        return;
    }

    const response = await fetch('/api/v1/run-extractor', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            fem_filename: femFile.name,
            mpcf_filename: mpcfFile.name,
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
