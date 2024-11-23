let mpcsData = []; // Global variable to store fetched data
let sortDirection = 1; // 1 for ascending, -1 for descending

async function fetchMPCs() {
    try {
        const response_rb2s = await fetch('/api/v1/rbe2s');
        const rbe2s = await response_rb2s.json();
        const response_rb3s = await fetch('/api/v1/rbe3s');
        const rbs3s = await response_rb3s.json();

        // Combine both rbe2s and rbe3s into mpcs
        mpcsData = rbe2s.concat(rbs3s);

        // Initially render the table with unsorted data
        renderTable(mpcsData);
    } catch (error) {
        console.error('Error fetching MPCs:', error);
    }
}

// Function to render the table
function renderTable(data) {
    const tableBody = document.getElementById('mpc-table-body');

    // Clear the table before appending new rows
    tableBody.innerHTML = '';

    data.forEach(mpc => {
        const row = document.createElement('tr');

        // Create individual table cells
        const idCell = document.createElement('td');
        idCell.textContent = mpc.id;

        const configCell = document.createElement('td');
        configCell.textContent = mpc.config;

        const masterNodeCell = document.createElement('td');
        masterNodeCell.textContent = mpc.master_node;

        const nodeCell = document.createElement('td');
        const slaveNodesButton = createCopyButton(mpc.nodes.split(",").join(", "), 'Copy Slave Nodes');
        nodeCell.appendChild(slaveNodesButton);

        // Create the part_id2nodes cell
        const partId2NodesCell = document.createElement('td');

        const partId2Nodes = mpc.part_id2nodes;

        partId2NodesCell.innerHTML = ""; // Clear content if any

        // Loop through the part_id2nodes dictionary
        for (const [partId, nodeIds] of Object.entries(partId2Nodes)) {
            if (nodeIds.length >= 1) {
                const label = document.createElement('span');
                label.textContent = `Part ${partId}: `;
                label.style.marginRight = '5px';

                const button = createCopyButton(nodeIds.join(", "), `Copy Nodes`);
                button.style.marginBottom = '5px';
                button.style.marginRight = '10px';

                partId2NodesCell.appendChild(label);
                partId2NodesCell.appendChild(button);
                partId2NodesCell.appendChild(document.createElement('br'));
            }
        }

        // Create the part_id2forces cell
        const partId2ForcesCell = document.createElement('td');
        const subcase_id2part_id2forces = mpc.subcase_id2part_id2forces;

        for (const [subcaseId, partId2Forces] of Object.entries(subcase_id2part_id2forces)) {
            for (const [partId, forces] of Object.entries(partId2Forces)) {
                const nodeIds = mpc.part_id2nodes[partId];
                if (!nodeIds || nodeIds.length === 0) continue;

                const force = Math.sqrt(
                    forces[0] ** 2 +
                    forces[1] ** 2 +
                    forces[2] ** 2
                ).toFixed(4);

                const label = document.createElement('span');
                label.textContent = `Subcase ${subcaseId}, Part ${partId}: ${force} `;
                label.style.marginRight = '5px';

                partId2ForcesCell.appendChild(label);
                partId2ForcesCell.appendChild(document.createElement('br'));
            }
        }

        // Append cells to the row
        row.appendChild(idCell);
        row.appendChild(configCell);
        row.appendChild(masterNodeCell);
        row.appendChild(nodeCell); // Add the slaveNodesButton cell
        row.appendChild(partId2NodesCell); // Add the partId2Nodes cell
        row.appendChild(partId2ForcesCell);

        // Append row to the table body
        tableBody.appendChild(row);
    });
}

function sortTableById() {
    // Toggle sorting direction
    sortDirection *= -1;

    // Sort the global data array
    mpcsData.sort((a, b) => (a.id - b.id) * sortDirection);

    // Re-render the table with sorted data
    renderTable(mpcsData);

    // Update the sorting icon
    const sortIcon = document.getElementById('id-sort-icon');
    if (sortDirection === 1) {
        sortIcon.textContent = '▲'; // Ascending
    } else {
        sortIcon.textContent = '▼'; // Descending
    }
}

// Attach sorting functionality to the ID column header
document.addEventListener('DOMContentLoaded', () => {
    const idHeader = document.querySelector('th[data-sort="id"]');
    if (idHeader) {
        idHeader.addEventListener('click', sortTableById);
    }
});



// Automatically fetch MPCs when the page loads
window.onload = fetchMPCs;