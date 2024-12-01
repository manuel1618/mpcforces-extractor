let currentPage = 1;  // Track the current page
let total_pages = 0;  // Track the total number of pages
const SPCS_PER_PAGE = 100;
let allSPCs = [];
let sortColumn = "node_id"; // Default sort column
let sortDirection = 1; // 1 for ascending, -1 for descending
let cachedSubcases = null;
const filterInput = document.getElementById('filter-id'); // used multiple times
const subcaseDropdown = document.getElementById('subcase-dropdown'); // used multiple times

async function fetchAllSPCs() {
    if (allSPCs.length > 0) return; // Skip fetching if data already exists
    
    const response = await safeFetch('/api/v1/spcs/all', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ids: [] })
    });

    if (!response.ok) {
        displayError('Error fetching SPCs.');
        return;
    }
    allSPCs = await response.json();
    total_pages = Math.ceil(allSPCs.length / SPCS_PER_PAGE);
}

/**
 * Used for recalculating the total pages when the filter is applied
 * @returns 
 */
async function fetchAllFilteredSPCs() {
    const filterData = parseFilterData(filterInput.value);
    const response = await safeFetch('/api/v1/spcs/all', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ids: filterData })
    });
    if (response == null){
        displayError('Error fetching SPCs.');
        addSPCsToTable([]); // Clear the table
        return
    }

    const allFilteredSPCs = await response.json();
    console.log(allFilteredSPCs);
    total_pages = Math.ceil(allFilteredSPCs.length / SPCS_PER_PAGE);
}



async function fetchSPCs(page = 1) {
    const filterData = parseFilterData(filterInput.value);
    await fetchAndRenderSPCs({ page, filterData });
}

async function filterSPCs() {
    currentPage = 1; // Reset to first page
    await fetchAllFilteredSPCs();
    await fetchAndRenderSPCs({ page: currentPage, filterData: parseFilterData(filterInput.value) });
    updatePagination();
}

async function resetSPCs() {
    filterInput.value = '';
    currentPage = 1;
    await fetchAndRenderSPCs({ page: currentPage });
    total_pages = Math.ceil(allSPCs.length / SPCS_PER_PAGE);
    updatePagination();
}


async function fetchAndRenderSPCs({ page = 1, filterData = [], subcaseId = 0, sortColumnOverride = null, sortDirectionOverride = null } = {}) {
    try {
        const queryParams = new URLSearchParams({
            page: page.toString(),
            sortColumn: sortColumnOverride || sortColumn,
            sortDirection: sortDirectionOverride || sortDirection,
        });

        const fetch_options = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ids: filterData })
        };

        const response = await safeFetch(`/api/v1/spcs?${queryParams.toString()}`, fetch_options);
        if (!response.ok) {
            displayError('Error fetching SPCs.');
            return;
        }

        const nodes = await response.json();

        if (Array.isArray(nodes) && nodes.length > 0) {
            addSPCsToTable(nodes);
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
            addSPCsToTable([]);
        }
    } catch (error) {
        displayError('Error fetching SPCs.');
    }
}


async function addSPCsToTable(spcs) {
    const tableBody = document.getElementById('spc-table-body');
    tableBody.innerHTML = '';

    if (!spcs || spcs.detail === "Not Found") {
        const row = document.createElement('tr');
        const cell = document.createElement('td');
        cell.colSpan = 6;
        cell.textContent = 'No spcs found';
        row.appendChild(cell);
        tableBody.appendChild(row);
        return;
    }

    const subcases = cachedSubcases || await fetchSubcases();
    const subcase = subcases.find(subcase => subcase.id == subcaseDropdown.value);
    
    const fragment = document.createDocumentFragment();
    spcs.forEach(spc => {
        const force = subcase?.node_id2spcforces[spc.node_id] || [0.0, 0.0, 0.0, 0.0, 0.0, 0.0];
        const row = document.createElement('tr');
        const dofs = spc.dofs;

        dof1 = dofs["1"];
        dof2 = dofs["2"];
        dof3 = dofs["3"];
        dof4 = dofs["4"];
        dof5 = dofs["5"];
        dof6 = dofs["6"];

        if (dof1 == null) {
            dof1 = "n/a";
        }
        if (dof2 == null) {
            dof2 = "n/a";
        }
        if (dof3 == null) {
            dof3 = "n/a";
        }
        if (dof4 == null) {
            dof4 = "n/a";
        }
        if (dof5 == null) {
            dof5 = "n/a";
        }
        if (dof6 == null) {
            dof6 = "n/a";
        }

        row.innerHTML = `
            <td>${spc.node_id}</td>
            <td>${spc.system_id}</td>
            <td>${dof1}</td>
            <td>${dof2}</td>
            <td>${dof3}</td>
            <td>${dof4}</td>
            <td>${dof5}</td>
            <td>${dof6}</td>
            <td>${force[0].toFixed(3)}</td>
            <td>${force[1].toFixed(3)}</td>
            <td>${force[2].toFixed(3)}</td>
            <td>${calculateForceMagnitude(force).linear}</td>
            <td>${force[3].toFixed(3)}</td>
            <td>${force[4].toFixed(3)}</td>
            <td>${force[5].toFixed(3)}</td>
            <td>${calculateForceMagnitude(force).moment}</td>

        `;
        fragment.appendChild(row);
    });

    tableBody.appendChild(fragment);
}



async function updateSortIcons() {
    const sortableHeaders = document.querySelectorAll('th[data-sort]');
    sortableHeaders.forEach(header => {
        const column = header.getAttribute('data-sort');
        const icon = header.querySelector('span');
        icon.textContent = (sortColumn === column) ? (sortDirection === 1 ? '▲' : '▼') : '↕'; // Default to bi-directional
    });
}



// Filter nodes by ID
document.getElementById('filter-by-node-id-button').addEventListener('click', async () => {
    filterSPCs()
});


filterInput.addEventListener('keyup', async (event) => {
    if (event.key === 'Enter') {
        filterSPCs();
    } else if (event.key === 'Escape') {
        filterInput.value = '';
        resetSPCs();
    }
});

// Reset filter and display all SPCs
document.getElementById('filter-reset-button').addEventListener('click', () => {
    resetSPCs()
});

function updatePagination() {
    const prevButton = document.getElementById('prev-button');
    const nextButton = document.getElementById('next-button');
    const paginationInfo = document.getElementById('pagination-info');

    prevButton.disabled = (currentPage === 1);
    nextButton.disabled = (total_pages === 1 || currentPage === total_pages);
    paginationInfo.textContent = `Page ${currentPage} of ${total_pages}`;
}

document.getElementById('prev-button').addEventListener('click', async () => {
    if (currentPage > 1) {
        currentPage -= 1;
        await fetchSPCs(currentPage);
    }
    updatePagination();
});

document.getElementById('next-button').addEventListener('click', async () => {
    if (currentPage < total_pages) {
        currentPage += 1;
        await fetchSPCs(currentPage);
    }
    updatePagination();
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
        await fetchSPCs(currentPage);
        updateSortIcons();
    });
});

document.addEventListener('DOMContentLoaded', async () => {
    await fetchSubcases();
    await fetchAllSPCs();

    if (allSPCs.length > 0) {
        currentPage = 1;
        await fetchSPCs(currentPage);
    }

    updatePagination();
    updateSortIcons();
});

document.getElementById('spcs-title').addEventListener('click', function() {
    location.reload(); // Reload the page
});