let currentPage = 1;  // Track the current page

async function fetchNodes(page = 1) {
    try {
        const response = await fetch(`/api/v1/nodes?page=${page}`);
        const nodes = await response.json();
        const tableBody = document.getElementById('node-table-body');

        // Clear the table before appending new rows
        tableBody.innerHTML = '';

        nodes.forEach(node => {
            const row = document.createElement('tr');

            const idCell = document.createElement('td');
            idCell.textContent = node.id;

            const coordsCell = document.createElement('td');
            coordsCell.textContent = `${node.coord_x}, ${node.coord_y}, ${node.coord_z}`;

            row.appendChild(idCell);
            row.appendChild(coordsCell);
            tableBody.appendChild(row);
        });

        currentPage = page;
        updatePaginationButtons();
    } catch (error) {
        console.error('Error fetching Nodes:', error);
    }
}

function updatePaginationButtons() {
    const prevButton = document.getElementById('prev-button');
    prevButton.disabled = (currentPage === 1);
}

document.getElementById('prev-button').addEventListener('click', () => {
    if (currentPage > 1) {
        fetchNodes(currentPage - 1);
    }
});

document.getElementById('next-button').addEventListener('click', () => {
    fetchNodes(currentPage + 1);
});

// Automatically fetch nodes when the page loads
window.onload = () => fetchNodes(1);
