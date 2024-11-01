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

