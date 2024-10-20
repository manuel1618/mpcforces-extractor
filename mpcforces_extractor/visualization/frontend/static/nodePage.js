let currentPage = 1;  // Track the current page
let total_pages = 0;  // Track the total number of pages
const NODES_PER_PAGE = 100;
let allNodes = [];

async function fetchAllNodes() {
    try {
        const response = await fetch('/api/v1/nodes/all');  // Fetch all nodes without pagination
        const nodes = await response.json();
        allNodes = nodes;  // Store all nodes for client-side filtering
        total_pages = Math.ceil(nodes.length / NODES_PER_PAGE);

        displayNodes(nodes);  // Initially display all nodes
    } catch (error) {
        console.error('Error fetching all Nodes:', error);
    }
}

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

            const coordsXCell = document.createElement('td');
            coordsXCell.textContent = node.coord_x;
            const coordsYCell = document.createElement('td');
            coordsYCell.textContent = node.coord_y;
            const coordsZCell = document.createElement('td');
            coordsZCell.textContent = node.coord_z;

            row.appendChild(idCell);
            row.appendChild(coordsXCell);
            row.appendChild(coordsYCell);
            row.appendChild(coordsZCell);

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
        currentPage -= 1;
    }
    updatePageNumber();
});

document.getElementById('next-button').addEventListener('click', () => {
    fetchNodes(currentPage + 1);
    currentPage += 1;
    updatePageNumber();
});

// update the page number, id: pagination-info (Page 1 of X)
function updatePageNumber() {
    const paginationInfo = document.getElementById('pagination-info');
    paginationInfo.textContent = `Page ${currentPage} of ${total_pages}`;
}



// Automatically fetch nodes when the page loads, and fetch all nodes if there are no total pages
document.addEventListener('DOMContentLoaded', () => {
    fetchNodes();
    if (total_pages === 0) {
        fetchAllNodes();
    }
});
