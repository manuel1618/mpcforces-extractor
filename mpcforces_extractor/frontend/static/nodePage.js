let currentPage = 1;  // Track the current page
let total_pages = 0;  // Track the total number of pages
const NODES_PER_PAGE = 100;
let allNodes = [];
let sortColumn = "id"; // Default sort column
let sortDirection = 1; // 1 for ascending, -1 for descending
let cachedSubcases = null;
let nodes = [];


async function fetchAllNodes() {
    try {
        const nodes = await safeFetch('/api/v1/nodes/all');
        allNodes = nodes;  // Store all nodes for client-side filtering
        if (nodes.length > 0) {
            total_pages = Math.ceil(nodes.length / NODES_PER_PAGE);
        } 
    } catch (error) {
        displayError('Error fetching all Nodes.}');
    }
}



async function fetchSubcases() {
    if (cachedSubcases) return cachedSubcases; // Use cached data if available
    try {
        cachedSubcases = await safeFetch('/api/v1/subcases');	
        populateSubcaseDropdown(cachedSubcases);
        return cachedSubcases;
    } catch (error) {
        displayError('Error fetching Subcases.');
        return [];
    }
}

function populateSubcaseDropdown(subcases) {
    const subcaseDropdown = document.getElementById('subcase-dropdown');
    subcaseDropdown.innerHTML = '';
    subcases.forEach(subcase => {
        const option = document.createElement('option');
        option.value = subcase.id;
        option.textContent = subcase.id;
        subcaseDropdown.appendChild(option);
    });
}

async function fetchNodes(page = 1) {
    try {
        let subcaseId = 0;
        if (sortColumn === 'fabs' || sortColumn === 'mabs') {
            subcaseId = document.getElementById('subcase-dropdown').value;
        }
        let  nodes = await safeFetch(`/api/v1/nodes?page=${page}&sortColumn=${sortColumn}&sortDirection=${sortDirection}&subcaseId=${subcaseId}`);
        if (nodes.length > 0) {
            addNodesToTable(nodes);
            currentPage = page;
            updatePaginationButtons();
            updateSortIcons();
        }
    } catch (error) {
        displayError('Error fetching Nodes.');
    }
}




async function addNodesToTable(nodes) {

    // Check if nodes is empty
    if (nodes.detail === "Not Found") {
        const tableBody = document.getElementById('node-table-body');
        tableBody.innerHTML = '';
        const row = document.createElement('tr');
        const cell = document.createElement('td');
        cell.colSpan = 6;
        cell.textContent = 'No nodes found';
        row.appendChild(cell);
        tableBody.appendChild(row);
        return;
    }


    // Clear the table before appending new rows
    const tableBody = document.getElementById('node-table-body');
    tableBody.innerHTML = '';

    // Info for forces
    const subcaseId = document.getElementById('subcase-dropdown').value;
    // Use cachedSubcases instead of refetching subcases
    const subcases = cachedSubcases || await fetchSubcases();
    const subcase = subcases.find(subcase => subcase.id == subcaseId);

    nodes.forEach(node => {
        const row = document.createElement('tr');

        const idCell = document.createElement('td');
        idCell.textContent = node.id;

        const coordsXCell = document.createElement('td');
        coordsXCell.textContent = node.coord_x.toFixed(3);
        const coordsYCell = document.createElement('td');
        coordsYCell.textContent = node.coord_y.toFixed(3);
        const coordsZCell = document.createElement('td');
        coordsZCell.textContent = node.coord_z.toFixed(3);

        
        const forsAbsCell = document.createElement('td');
        const momentAbsCell = document.createElement('td');
        try {
            forces = subcase.node_id2forces[node.id];
        } catch (error) {
            forces = undefined
        }   
        if (forces === undefined) {
            forces = [0, 0, 0, 0, 0, 0];
        }
        const { linear, moment } = calculateForceMagnitude(subcase?.node_id2forces[node.id] || []);
        forsAbsCell.textContent = linear;
        momentAbsCell.textContent = moment;

        row.appendChild(idCell);
        row.appendChild(coordsXCell);
        row.appendChild(coordsYCell);
        row.appendChild(coordsZCell);
        row.appendChild(forsAbsCell);
        row.appendChild(momentAbsCell);

        tableBody.appendChild(row);
    });
}

function calculateForceMagnitude(forces = [0, 0, 0, 0, 0, 0]) {
    const linear = Math.sqrt(forces[0]**2 + forces[1]**2 + forces[2]**2).toFixed(2);
    const moment = Math.sqrt(forces[3]**2 + forces[4]**2 + forces[5]**2).toFixed(2);
    return { linear, moment };
}




// Filter nodes by ID
document.getElementById('filter-by-node-id-button').addEventListener('click', async () => {
    filterNodes()
});

// Filter nodes by ID when the user presses Enter
document.getElementById('filter-id').addEventListener('keyup', async (event) => {
    if (event.key === 'Enter') {
        filterNodes();
    }
});

// Reset if the user presses Escape
document.getElementById('filter-id').addEventListener('keyup', (event) => {
    if (event.key === 'Escape') {
        document.getElementById('filter-id').value = '';
        resetNodes();
    }
});

async function filterNodes() {
    const filterData = document.getElementById('filter-id').value
    .trim()
    .split(",")
    .map(a => a.trim());


    nodes = await safeFetch('/api/v1/nodes/filter', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ids: filterData }),
    });
    addNodesToTable(nodes);
    
    // hide the page buttons and pagination info
    document.getElementById('next-button').style.display = 'none';
    document.getElementById('prev-button').style.display = 'none';
    document.getElementById('pagination-info').textContent = '';

    updatePaginationButtons();
}

// Reset filter and display all nodes
document.getElementById('filter-reset-button').addEventListener('click', () => {
    resetNodes()
});

async function resetNodes() {
    await fetchNodes(1);
    await fetchAllNodes();
    total_pages = Math.ceil(allNodes.length / NODES_PER_PAGE);
    updatePageNumber();

    // show the page buttons and pagination info
    document.getElementById('next-button').style.display = 'block';
    document.getElementById('prev-button').style.display = 'block';
    document.getElementById('filter-id').value = '';
};

function updatePaginationButtons() {
    const prevButton = document.getElementById('prev-button');
    prevButton.disabled = (currentPage === 1);
    const nextButton = document.getElementById('next-button');
    nextButton.disabled = (total_pages === 1) || (currentPage === total_pages);
}

async function safeFetch(url, options = {}) {
    try {
        const response = await fetch(url, options);
        if (!response.ok) throw new Error(`${response.status}: ${response.statusText}`);
        return await response.json();
    } catch (error) {
        displayError(`Error fetching ${url}: ${error}`);
        return null;
    }
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

async function updateSortIcons() {
    const sortableHeaders = document.querySelectorAll('th[data-sort]');
    sortableHeaders.forEach(header => {
        const column = header.getAttribute('data-sort');
        const icon = header.querySelector('span');
        icon.textContent = (sortColumn === column) ? (sortDirection === 1 ? '▲' : '▼') : '▲▼';
    });
}

document.querySelectorAll('th[data-sort]').forEach(header => {
    header.addEventListener('click', async () => {
        let column = header.getAttribute('data-sort');

        // Update sort direction and column
        if (column === sortColumn) {
            sortDirection *= -1; // Toggle the sort direction
        } else {
            sortColumn = column; // Change to the clicked column
            sortDirection = 1;  // Default to ascending when switching columns
        }

        // Fetch the sorted nodes
        await fetchNodes(currentPage);
        updateSortIcons();
    });
});

function displayError(message) {
    const errorContainer = document.getElementById('error-container'); // Ensure an error container exists in HTML
    if (errorContainer) {
        errorContainer.textContent = message;
        errorContainer.style.display = 'block';
    } else {
        console.error(message); // Fallback
    }
}



document.addEventListener('DOMContentLoaded', async () => {
    fetchSubcases();
    if (total_pages === 0) {
        await fetchAllNodes();
        currentPage = 1;
        updatePageNumber();
        updateSortIcons();
        fetchNodes(currentPage);
    } else {
        updatePageNumber();
        updateSortIcons();
    }

});
