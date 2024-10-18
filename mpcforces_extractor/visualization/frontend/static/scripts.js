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

            const nodeCell = document.createElement('td');
            const slaveNodesButton = createCopyButton(mpc.nodes.split(",").join(", "), 'Copy Slave Nodes');
            nodeCell.appendChild(slaveNodesButton);

            // Create the part_id2nodes cell
            const partId2NodesCell = document.createElement('td');

            // Convert part_id2nodes dictionary into a set of copy buttons
            const partId2Nodes = mpc.part_id2nodes;

            // Clear any existing content in the partId2NodesCell (if necessary)
            partId2NodesCell.innerHTML = "";

            // Loop through the part_id2nodes dictionary and create buttons for each part's node IDs
            for (const [partId, nodeIds] of Object.entries(partId2Nodes)) {
                const nodesText = nodeIds.length > 0 ? nodeIds.join(", ") : "No nodes";

                // Create a label like "Part X: "
                const label = document.createElement('span');
                label.textContent = `Part ${partId}: `;
                label.style.marginRight = '5px'; // Add a little space between the label and the button

                // Use createCopyButton() to generate the button
                const button = createCopyButton(nodesText, `Copy Nodes`);

                // Add some margin to the button for spacing between them
                button.style.marginBottom = '5px';
                button.style.marginRight = '10px'; // Space between buttons

                // Append the label and button to the partId2NodesCell
                partId2NodesCell.appendChild(label);
                partId2NodesCell.appendChild(button);
                
                // Optional: Add a line break between sets for better readability
                partId2NodesCell.appendChild(document.createElement('br'));
            }


            // Create the part_id2forces cell


            const partId2ForcesCell = document.createElement('td');
            subcase_id2part_id2forces = mpc.subcase_id2part_id2forces;
            for (const [subcaseId,partId2Forces] of Object.entries(subcase_id2part_id2forces)) {
                for (const [partId, forces] of Object.entries(partId2Forces)) {
                    force_x = parseFloat(forces[0]);
                    force_y = parseFloat(forces[1]);
                    force_z = parseFloat(forces[2]);
                    force = Math.sqrt(force_x**2 + force_y**2 + force_z**2);
                    force = force.toFixed(4);

                    // Create a label like "Part X: "
                    const label = document.createElement('span');
                    label.textContent = `Subcase ${subcaseId}, Part ${partId}: ${force} `;
                    label.style.marginRight = '5px'; // Add a little space between the label and the button
                    // Append the label and button to the partId2NodesCell
                    partId2ForcesCell.appendChild(label);
                    partId2ForcesCell.appendChild(document.createElement('br'));
                }
            }



            // Append cells to the row
            row.appendChild(idCell);
            row.appendChild(masterNodeCell);
            row.appendChild(nodeCell); // Add the slaveNodesButton cell
            row.appendChild(partId2NodesCell); // Add the partId2Nodes cell
            row.appendChild(partId2ForcesCell);

            // Append row to the table body
            tableBody.appendChild(row);
        });
    } catch (error) {
        console.error('Error fetching MPCs:', error);
    }
}

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



document.addEventListener('DOMContentLoaded', function() {
    const toggleButton = document.getElementById('dark-mode-toggle');
    const body = document.body;

    // Check localStorage for the theme and apply it
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        body.classList.add('dark-mode');
        toggleButton.textContent = 'Light Mode';
    }

    // Dark mode toggle functionality
    toggleButton.addEventListener('click', () => {
        // Toggle between light and dark mode
        body.classList.toggle('dark-mode');

        // Save the current mode in localStorage
        if (body.classList.contains('dark-mode')) {
            localStorage.setItem('theme', 'dark');
            toggleButton.textContent = 'Light Mode';
        } else {
            localStorage.setItem('theme', 'light');
            toggleButton.textContent = 'Dark Mode';
        }
    });
});
