async function fetchNodes() {
    try {
        const response = await fetch('/api/v1/nodes');
        const nodes = await response.json();
        const tableBody = document.getElementById('node-table-body');

        // Clear the table before appending new rows
        tableBody.innerHTML = '';

        nodes.forEach(node => {
            const row = document.createElement('tr');

            // Create individual table cells
            const idCell = document.createElement('td');
            idCell.textContent = node.id;

            const coordsCell = document.createElement('td');
            coordsCell.textContent = `${node.coord_x}, ${node.coord_y}, ${node.coord_z}`;

            // Append cells to the row
            row.appendChild(idCell);
            row.appendChild(coordsCell);

            // Append row to the table body
            tableBody.appendChild(row);
        });
    } catch (error) {
        console.error('Error fetching Nodes:', error);
    }
}




async function fetchMPCs() {
    try {
        const response = await fetch('/api/v1/mpcs');
        const mpcs = await response.json();
        const tableBody = document.getElementById('mpc-table-body');

        // Clear the table before appending new rows
        tableBody.innerHTML = '';

        mpcs.forEach(mpc => {
            const row = document.createElement('tr');

            // Create individual table cells
            const idCell = document.createElement('td');
            idCell.textContent = mpc.id;

            const masterNodeCell = document.createElement('td');
            masterNodeCell.textContent = mpc.master_node;

            const nodesCell = document.createElement('td');
            nodesCell.textContent = mpc.nodes.split(",").join(", ");

            // Create the visualization script cell with a button
            const scriptCell = document.createElement('td');
            const copyButton = document.createElement('button');
            copyButton.className = 'btn btn-secondary btn-sm';
            copyButton.textContent = 'Copy Script';

            // Placeholder visualization script (customize this as needed)
            const visualizationScript = `Visualize MPC ${mpc.id} with Master Node ${mpc.master_node} and Nodes ${mpc.nodes}`;

            // Copy to clipboard function
            copyButton.addEventListener('click', () => {
                navigator.clipboard.writeText(visualizationScript).then(() => {
                    // Show a "Copied" message
                    const copiedMsg = document.createElement('span');
                    copiedMsg.textContent = 'Copied!';
                    copiedMsg.className = 'copied-msg';
                    scriptCell.appendChild(copiedMsg);

                    // Remove the message after 1.5 seconds
                    setTimeout(() => {
                        copiedMsg.remove();
                    }, 1500);
                }).catch(err => {
                    console.error('Failed to copy text:', err);
                });
            });

            // Append the button to the script cell
            scriptCell.appendChild(copyButton);

            // Append cells to the row
            row.appendChild(idCell);
            row.appendChild(masterNodeCell);
            row.appendChild(nodesCell);
            row.appendChild(scriptCell);

            // Append row to the table body
            tableBody.appendChild(row);
        });
    } catch (error) {
        console.error('Error fetching MPCs:', error);
    }
}

