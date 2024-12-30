let mpcsData = []; // Global variable to store fetched data
let sortDirection = 1; // 1 for ascending, -1 for descending
let currentPage = 1; // Track the current page
const MPCS_PER_PAGE = 10; // Number of MPCs per page
let total_pages = 0; // Total number of pages
let cachedSubcases = null;

const subcaseDropdown = document.getElementById('subcase-dropdown'); // used multiple times

async function fetchMPCs() {
    try {
        const response_rb2s = await fetch('/api/v1/rbe2s');
        const rbe2s = await response_rb2s.json();
        const response_rb3s = await fetch('/api/v1/rbe3s');
        const rbs3s = await response_rb3s.json();

        // Combine both rbe2s and rbe3s into mpcs
        mpcsData = rbe2s.concat(rbs3s);
        // sort mpcsData by id
        mpcsData.sort((a, b) => a.id - b.id);
        total_pages = Math.ceil(mpcsData.length / MPCS_PER_PAGE);

        // Initially render the table with unsorted data
        const mpcsDataSlice = getCurrentPageData();
        renderTable(mpcsDataSlice);
        updatePagination();
    } catch (error) {
        console.error('Error fetching MPCs:', error);
    }
}

function getCurrentPageData() {
    const startIndex = (currentPage - 1) * MPCS_PER_PAGE;
    const endIndex = startIndex + MPCS_PER_PAGE;
    return mpcsData.slice(startIndex, endIndex);
}

function updatePagination() {
    const prevButton = document.getElementById('prev-button');
    const nextButton = document.getElementById('next-button');
    const paginationInfo = document.getElementById('pagination-info');

    prevButton.disabled = currentPage === 1;
    nextButton.disabled = currentPage === total_pages;
    paginationInfo.textContent = `Page ${currentPage} of ${total_pages}`;
}

// Function to render the table
async function renderTable(data) {
    const tableBody = document.getElementById('mpc-table-body');

    cachedSubcases || await fetchSubcases(); // Fetch subcases if not already cached

    // Clear the table before appending new rows
    tableBody.innerHTML = '';

    data.forEach(mpc => {
        const partId2Forces = mpc.subcase_id2part_id2forces[subcaseDropdown.value];
        const partIdsSorted = Object.keys(partId2Forces).sort((a, b) => a - b);
    
        // Create the parent row for the MPC
        const parentRow = document.createElement('tr');
        parentRow.classList.add('parent-row'); // Add a class for styling
    
        // Parent row cells
        const idCell = document.createElement('td');
        idCell.textContent = mpc.id;
        idCell.rowSpan = partIdsSorted.length + 1;
        idCell.classList.add('centered'); // Center-align

        const configCell = document.createElement('td');
        configCell.textContent = mpc.config;
        configCell.rowSpan = partIdsSorted.length + 1;
        configCell.classList.add('centered'); // Center-align

        const masterNodeCell = document.createElement('td');
        masterNodeCell.textContent = mpc.master_node;
        masterNodeCell.rowSpan = partIdsSorted.length + 1;
        masterNodeCell.classList.add('centered'); // Center-align

        const nodeCell = document.createElement('td');
        const slaveNodesButton = createCopyButton(mpc.nodes.split(",").join(", "), 'Copy');
        nodeCell.appendChild(slaveNodesButton);
        nodeCell.rowSpan = partIdsSorted.length + 1;
        nodeCell.classList.add('centered'); // Center-align

        const diameterCell = document.createElement('td');
        diameterCell.textContent = styleNumber(mpc.diameter);
        diameterCell.rowSpan = partIdsSorted.length + 1;
        diameterCell.classList.add('centered'); // Center-align

        const lengthCell = document.createElement('td');
        lengthCell.textContent = styleNumber(mpc.length);
        lengthCell.rowSpan = partIdsSorted.length + 1;
        lengthCell.classList.add('centered'); // Center-align
        
        const maxShearCell = document.createElement('td');
        maxShearCell.textContent = styleNumber(mpc.max_shear);
        maxShearCell.rowSpan = partIdsSorted.length + 1;
        maxShearCell.classList.add('centered'); // Center-align

        const maxNormalStressCell = document.createElement('td');
        maxNormalStressCell.textContent = styleNumber(mpc.max_norm);
        maxNormalStressCell.rowSpan = partIdsSorted.length + 1;
        maxNormalStressCell.classList.add('centered'); // Center-align
    
        // Append parent row cells
        parentRow.appendChild(idCell);
        parentRow.appendChild(configCell);
        parentRow.appendChild(masterNodeCell);
        parentRow.appendChild(nodeCell);
        parentRow.appendChild(diameterCell);
        parentRow.appendChild(lengthCell);
        parentRow.appendChild(maxShearCell);
        parentRow.appendChild(maxNormalStressCell);
        tableBody.appendChild(parentRow);
    
        // Add sub-rows for each part
        for (const partId of partIdsSorted) {
            const row = document.createElement('tr');
            row.classList.add('sub-row'); // Add a class for styling
    
            const partCell = document.createElement('td');
            partCell.textContent = partId;
    
            const forces = partId2Forces[partId];
            const fxCell = document.createElement('td');
            fxCell.textContent = styleNumber(forces[0]);
            const fyCell = document.createElement('td');
            fyCell.textContent = styleNumber(forces[1]);
            const fzCell = document.createElement('td');
            fzCell.textContent = styleNumber(forces[2]);
    
            const fAbsCell = document.createElement('td');
            fAbsCell.textContent = styleNumber(Math.sqrt(forces[0]**2 + forces[1]**2 + forces[2]**2));
            const mAbsCell = document.createElement('td');
            mAbsCell.textContent = styleNumber(Math.sqrt(forces[3]**2 + forces[4]**2 + forces[5]**2));
    
            // Append cells to the sub-row
            row.appendChild(partCell);
            row.appendChild(fxCell);
            row.appendChild(fyCell);
            row.appendChild(fzCell);
            row.appendChild(fAbsCell);
            row.appendChild(mAbsCell);
    
            tableBody.appendChild(row);
        }


    });
    
}

function styleNumber(force) {
    if (force === 0) {
        return '0';
    }
    if (Math.abs(force) > 0.1 && Math.abs(force) < 10000) {
        return force.toFixed(2);
    }
    return force.toExponential(2);
}

async function sortTableById() {
    // Toggle sorting direction
    sortDirection *= -1;

    // Sort the global data array
    mpcsData.sort((a, b) => (a.id - b.id) * sortDirection);

    // Re-render the table with sorted data
    await renderTable(mpcsData);

    // Update the sorting icon
    const sortIcon = document.getElementById('id-sort-icon');
    if (sortDirection === 1) {
        sortIcon.textContent = '▲'; // Ascending
    } else {
        sortIcon.textContent = '▼'; // Descending
    }
}

// Filter stuff
function resetFilter() {
    document.getElementById('mpc-filter-input').value = ''; // Clear input
    renderTable(mpcsData); // Render the original data
}

function filterMPCs() {
    const filterField = document.getElementById('filter-field-select').value; // Field to filter by
    const filterValue = document.getElementById('mpc-filter-input').value.trim().toLowerCase(); // User input

    // Filter the mpcsData based on the selected field and value
    const filteredData = mpcsData.filter(mpc => {
        const fieldValue = mpc[filterField]?.toString().toLowerCase(); // Field value in lowercase
        return fieldValue.includes(filterValue); // Check for match
    });

    // Render the filtered data
    renderTable(filteredData);
}


// Attach sorting functionality to the ID column header
document.addEventListener('DOMContentLoaded', () => {
    const idHeader = document.querySelector('th[data-sort="id"]');
    if (idHeader) {
        idHeader.addEventListener('click', sortTableById);
    }
    fetchMPCs();
});

document.getElementById('mpcs-title').addEventListener('click', function() {
    location.reload(); // Reload the page
});

document.getElementById('prev-button').addEventListener('click', () => {
    if (currentPage > 1) {
        currentPage--;
        renderTable(getCurrentPageData());
        updatePagination();
    }
});

document.getElementById('next-button').addEventListener('click', () => {
    if (currentPage < total_pages) {
        currentPage++;
        renderTable(getCurrentPageData());
        updatePagination();
    }
});

// Apply filter
document.getElementById('apply-filter-button').addEventListener('click', () => {
    filterMPCs();
});

// Reset filter
document.getElementById('reset-filter-button').addEventListener('click', () => {
    resetFilter();
});

// Optional: Trigger filtering on pressing "Enter" in the input field
document.getElementById('mpc-filter-input').addEventListener('keyup', event => {
    if (event.key === 'Enter') {
        filterMPCs();
    }
    if (event.key === 'Escape') {
        resetFilter();
    }
});
