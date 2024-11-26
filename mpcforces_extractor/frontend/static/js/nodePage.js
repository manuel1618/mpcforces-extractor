let currentPage = 1;  // Track the current page
let total_pages = 0;  // Track the total number of pages
const NODES_PER_PAGE = 100;
let allNodes = [];
let sortColumn = "id"; // Default sort column
let sortDirection = 1; // 1 for ascending, -1 for descending
let cachedSubcases = null;
const filterInput = document.getElementById('filter-id'); // used multiple times
const subcaseDropdown = document.getElementById('subcase-dropdown'); // used multiple times

async function fetchSubcases() {
    if (cachedSubcases) return cachedSubcases; // Use cached data if available
    const response = await safeFetch('/api/v1/subcases');
    if (!response.ok) {
        displayError('Error fetching Subcases.');
        return [];
    }
    cachedSubcases = await response.json();
    populateSubcaseDropdown(cachedSubcases);
    return cachedSubcases;
}

async function fetchAllNodes() {
    const response = await safeFetch('/api/v1/nodes/all');
    if (!response.ok) {
        displayError('Error fetching Nodes.');
        return;
    }
    allNodes = await response.json();
    if (allNodes.length) {
        total_pages = Math.ceil(allNodes.length / NODES_PER_PAGE);
    }
}

function populateSubcaseDropdown(subcases) {
    subcaseDropdown.innerHTML = '';
    subcases.forEach(subcase => {
        const option = document.createElement('option');
        option.value = subcase.id;
        option.textContent = subcase.id;
        subcaseDropdown.appendChild(option);
    });
}

async function fetchNodes(page = 1) {
    const subcaseId = (sortColumn === 'fabs' || sortColumn === 'mabs')
        ? subcaseDropdown.value
        : 0;

    const filterData = parseFilterData(filterInput.value);
    await fetchAndRenderNodes({ page, filterData, subcaseId });
}

async function filterNodes() {
    const filterData = parseFilterData(filterInput.value);
    currentPage = 1; // Reset to first page when filtering
    await fetchAndRenderNodes({ page: currentPage, filterData });
}

async function resetNodes() {
    filterInput.value = '';
    currentPage = 1; // Reset to first page when resetting
    await fetchAllNodes(); // Pre-fetch all data if necessary
    await fetchAndRenderNodes({ page: currentPage });
}

async function fetchAndRenderNodes({ page = 1, filterData = [], subcaseId = 0, sortColumnOverride = null, sortDirectionOverride = null } = {}) {
    try {
        const queryParams = new URLSearchParams({
            page: page.toString(),
            sortColumn: sortColumnOverride || sortColumn,
            sortDirection: sortDirectionOverride || sortDirection,
            subcaseId: subcaseId?.toString() || ""
        });

        const fetch_options = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ids: filterData })
        };

        const response = await safeFetch(`/api/v1/nodes?${queryParams.toString()}`, fetch_options);
        if (!response.ok) {
            displayError('Error fetching Nodes.');
            return;
        }

        const nodes = await response.json();

        if (Array.isArray(nodes) && nodes.length > 0) {
            addNodesToTable(nodes);
            currentPage = page;
            // update pagination
            const prevButton = document.getElementById('prev-button');
            prevButton.disabled = (currentPage === 1);
            const nextButton = document.getElementById('next-button');
            nextButton.disabled = (total_pages === 1) || (currentPage === total_pages);
            // sort
            updateSortIcons();
        } else {
            // Handle empty state
            addNodesToTable([]);
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
    const subcaseId = subcaseDropdown.value;
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

function calculateForceMagnitude(forces) {
    const linear = Math.sqrt(forces[0]**2 + forces[1]**2 + forces[2]**2).toFixed(2);
    const moment = Math.sqrt(forces[3]**2 + forces[4]**2 + forces[5]**2).toFixed(2);
    return { linear, moment };
}


async function updateSortIcons() {
    const sortableHeaders = document.querySelectorAll('th[data-sort]');
    sortableHeaders.forEach(header => {
        const column = header.getAttribute('data-sort');
        const icon = header.querySelector('span');
        icon.textContent = (sortColumn === column) ? (sortDirection === 1 ? '▲' : '▼') : '↕'; // Default to bi-directional
    });
}

// update the page number, id: pagination-info (Page 1 of X)
function updatePageNumber() {
    const paginationInfo = document.getElementById('pagination-info');
    paginationInfo.textContent = `Page ${currentPage} of ${total_pages}`;
}

function displayError(message) {
    const errorContainer = document.getElementById('error-container'); // Ensure an error container exists in HTML
    if (errorContainer) {
        errorContainer.textContent = message;
        errorContainer.style.display = 'block';
    } else {
        console.error(message); // Fallback
    }
}

function parseFilterData(inputElement) {
    return inputElement
        .trim()
        .split(",")
        .map(a => a.trim())
        .filter(a => a !== "");
}

// Filter nodes by ID
document.getElementById('filter-by-node-id-button').addEventListener('click', async () => {
    filterNodes()
});


filterInput.addEventListener('keyup', async (event) => {
    if (event.key === 'Enter') {
        filterNodes();
    } else if (event.key === 'Escape') {
        filterInput.value = '';
        resetNodes();
    }
});

// Reset filter and display all nodes
document.getElementById('filter-reset-button').addEventListener('click', () => {
    resetNodes()
});


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

document.addEventListener('DOMContentLoaded', async () => {
    fetchSubcases();
    if (total_pages === 0) {
        await fetchAllNodes();
        total_pages = Math.ceil(allNodes.length / NODES_PER_PAGE);
        currentPage = 1;
        await fetchNodes(currentPage);
    } 
    updateSortIcons();
    updatePageNumber();
});
