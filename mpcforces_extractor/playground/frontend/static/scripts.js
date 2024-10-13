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
        
        // Log the MPC data to check if it's being fetched properly
        console.log("MPCs fetched:", mpcs);

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

            // Log part_id2nodes to ensure it's correct
            console.log("Part ID to Nodes for MPC", mpc.id, ":", mpc.part_id2nodes);

            // Create the part_id2nodes cell
            const partId2NodesCell = document.createElement('td');

            // Convert part_id2nodes dictionary into a readable format
            const partId2Nodes = mpc.part_id2nodes;
            let partId2NodesText = "";

            // Loop through the part_id2nodes dictionary
            for (const [partId, nodeIds] of Object.entries(partId2Nodes)) {
                if (nodeIds.length > 0) {
                    partId2NodesText += `Part ${partId}: ${nodeIds.join(", ")}<br>`;
                } else {
                    partId2NodesText += `Part ${partId}: No nodes<br>`;
                }
            }

            // Set the text of the partId2NodesCell
            partId2NodesCell.innerHTML = partId2NodesText;

            // Create the visualization script cell with a button
            const scriptCell = document.createElement('td');
            const copyButton = document.createElement('button');
            copyButton.className = 'btn btn-secondary btn-sm';
            copyButton.textContent = 'Copy Script';

            // Placeholder visualization script
            const visualizationScript = `Visualize MPC ${mpc.id} with Master Node ${mpc.master_node} and Nodes ${mpc.nodes}`;

            // Copy to clipboard function
            copyButton.addEventListener('click', () => {
                navigator.clipboard.writeText(visualizationScript).then(() => {
                    // Store the original text
                    const originalText = copyButton.textContent;

                    // Change the button text to 'Copied!' and update its style
                    copyButton.textContent = 'Copied!';
                    copyButton.style.backgroundColor = '#4CAF50'; // Change background to green
                    copyButton.style.color = '#fff'; // Change text color to white

                    // Revert back to original text after 1.5 seconds
                    setTimeout(() => {
                        copyButton.textContent = originalText;
                        copyButton.style.backgroundColor = ''; // Reset to original background
                        copyButton.style.color = ''; // Reset to original text color
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
            row.appendChild(partId2NodesCell); // Add the partId2Nodes cell
            row.appendChild(scriptCell);

            // Append row to the table body
            tableBody.appendChild(row);
        });
    } catch (error) {
        console.error('Error fetching MPCs:', error);
    }
}
