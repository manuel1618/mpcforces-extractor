let currentPage = 1;  // Track the current page
let total_pages = 0;  // Track the total number of pages
const NODES_PER_PAGE = 100;
let allNodes = [];
let sortColumn = 'id'; // Default sort column
let sortDirection = 1; // 1 for ascending, -1 for descending



async function fetchAllNodes() {
    try {
        const response = await fetch('/api/v1/nodes/all');  // Fetch all nodes without pagination
        const nodes = await response.json();
        allNodes = nodes;  // Store all nodes for client-side filtering
        if (nodes.length > 0) {
            total_pages = Math.ceil(nodes.length / NODES_PER_PAGE);
        } 
    } catch (error) {
        console.error('Error fetching all Nodes:', error);
    }
}

async function fetchSubcases(){
    try {
        const response = await fetch('/api/v1/subcases');	
        const subcases = await response.json();
        // populate the Dropdown with Subcase ids
        const subcaseDropdown = document.getElementById('subcase-dropdown');
        subcaseDropdown.innerHTML = ''; // clear it before populating
        subcases.forEach(subcase => {
            const option = document.createElement('option');
            option.value = subcase.id;
            option.textContent = subcase.id;
            subcaseDropdown.appendChild(option);
        });
    } catch (error) {
        console.error('Error fetching Subcases:', error);
    }
}


async function fetchNodes(page = 1) {
    try {
        const response = await fetch(`/api/v1/nodes?page=${page}&sortColumn=${sortColumn}&sortDirection=${sortDirection}`);
        const nodes = await response.json();
        if (nodes.length > 0) {
            addNodesToTable(nodes);
            currentPage = page;
            updatePaginationButtons();
        }
    } catch (error) {
        console.error('Error fetching Nodes:', error);
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
    const response = await fetch('/api/v1/subcases');	
    const subcases = await response.json();
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
        try {
            forces = subcase.node_id2forces[node.id];
        } catch (error) {
            forces = undefined
        }   

        if (forces === undefined) {
            forces = [0, 0, 0, 0, 0, 0];
        }
        forsAbsCell.textContent = Math.sqrt(forces[0]**2 + forces[1]**2 + forces[2]**2).toFixed(2);

        const momentAbsCell = document.createElement('td');
        momentAbsCell.textContent = Math.sqrt(forces[3]**2 + forces[4]**2 + forces[5]**2).toFixed(2);


        row.appendChild(idCell);
        row.appendChild(coordsXCell);
        row.appendChild(coordsYCell);
        row.appendChild(coordsZCell);
        row.appendChild(forsAbsCell);
        row.appendChild(momentAbsCell);

        tableBody.appendChild(row);
    });
}



// fistering nodes by id
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

    try {
        const response = await fetch('/api/v1/nodes/filter', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ ids: filterData }),
        });
        
        if (!response.ok) {
            throw new Error(`Error: ${response.statusText}`);
        }
        
        const nodes = await response.json();
        addNodesToTable(nodes);
    } catch (error) {
        console.error('Error fetching Nodes:', error);
    }
    
    // hide the page buttons and pagination info
    document.getElementById('next-button').style.display = 'none';
    document.getElementById('prev-button').style.display = 'none';
    document.getElementById('pagination-info').textContent = '';
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
document.addEventListener('DOMContentLoaded', async () => {
    fetchSubcases();
    if (total_pages === 0) {
        await fetchAllNodes();
        currentPage = 1;
        updatePageNumber();
        console.log('Total pages:', total_pages);
    } else {
        await fetchNodes(1);
        updatePageNumber();
    }

    const sortableHeaders = document.querySelectorAll('th[data-sort]');
    sortableHeaders.forEach(header => {
        header.addEventListener('click', () => {
            const column = header.getAttribute('data-sort');

            if (column === 'x' || column === 'y' || column === 'z') {
                column = `coord_${column}`;
            }

            // Toggle direction if the same column is clicked
            if (sortColumn === column) {
                sortDirection *= -1;
            } else {
                sortColumn = column;
                sortDirection = 1; // Default to ascending
            }

            // Fetch sorted nodes and update the table
            fetchNodes(currentPage);

            // Update sorting icons
            updateSortIcons();
        });
    });
});


function updateSortIcons(sortColumn, sortDirection) {
    const sortableHeaders = document.querySelectorAll('th[data-sort]');
    console.log("Updating Sort Icons...");

    sortableHeaders.forEach(header => {
        const column = header.getAttribute('data-sort');
        const icon = header.querySelector('span'); // Get the span directly

        // Debug: print out the column being processed
        console.log(`Processing column: ${column}`);

        // If the column is the sorted column, show the correct icon
        if (sortColumn === column) {
            console.log(`Column ${column} is sorted. Direction: ${sortDirection === 1 ? 'Ascending' : 'Descending'}`);
            
            // Set the appropriate icon based on the sort direction
            if (column === 'id') {
                if (sortDirection === 1) {
                    icon.textContent = '▲'; // Ascending
                } else {
                    icon.textContent = '▼'; // Descending
                }
            } else if (column === 'x') {
                if (sortDirection === 1) {
                    icon.textContent = '▲'; // Ascending
                } else {
                    icon.textContent = '▼'; // Descending
                }
            } else if (column === 'y') {
                if (sortDirection === 1) {
                    icon.textContent = '▲'; // Ascending
                } else {
                    icon.textContent = '▼'; // Descending
                }
            } else if (column === 'z') {
                if (sortDirection === 1) {
                    icon.textContent = '▲'; // Ascending
                } else {
                    icon.textContent = '▼'; // Descending
                }
            }
        } else {
            console.log(`Column ${column} is not sorted. Resetting icon.`);
            // Reset icon if this column is not being sorted
            icon.textContent = '▲▼';
        }
    });
}

document.querySelectorAll('th[data-sort]').forEach(header => {
    header.addEventListener('click', () => {
        let column = header.getAttribute('data-sort');
        console.log(`Column clicked: ${column}`);
        
        // Adjust for coordinate columns
        if (column === 'x' || column === 'y' || column === 'z') {
            column = `coord_${column}`;
            console.log(`Adjusted column for coordinates: ${column}`);
        }

        // Toggle sorting direction if clicking the same column again
        if (sortColumn === column) {
            sortDirection *= -1; // Reverse the direction
            console.log(`Reversing sort direction. New direction: ${sortDirection === 1 ? 'Ascending' : 'Descending'}`);
        } else {
            sortColumn = column; // Set the new column to be sorted
            sortDirection = 1;    // Default to ascending if it's a new column
            console.log(`New column to sort by: ${column}. Defaulting to ascending.`);
        }

        // Fetch the sorted nodes
        fetchNodes(currentPage);

        // Update the sorting icons
        updateSortIcons(sortColumn, sortDirection);
    });
});

// Ensure that all headers have a sort icon when the page loads
document.addEventListener('DOMContentLoaded', () => {
    updateSortIcons();
});
