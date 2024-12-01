let spcclusters = []; // Global variable to store fetched data
let sortDirection = 1; // 1 for ascending, -1 for descending
let cachedSubcases = null; // Cache subcases to avoid fetching them multiple times
const subcaseDropdown = document.getElementById('subcase-dropdown'); // used multiple times

async function fetchSPCCluster() {
        const response = await safeFetch('/api/v1/spccluster');
        if (!response.ok) {
            displayError('Error fetching SPC Clusters.');
            return;
        }
        spcclusters = await response.json();
        renderTable(spcclusters);
}

async function fetchSubcases(forceRefresh = false) {
    if (!forceRefresh && cachedSubcases) return cachedSubcases; // Use cached data unless forced
    const response = await safeFetch('/api/v1/subcases');
    if (!response.ok) {
        displayError('Error fetching Subcases.');
        return [];
    }
    cachedSubcases = await response.json();
    populateSubcaseDropdown(cachedSubcases);
    return cachedSubcases;
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

// Function to render the table
async function renderTable(data) {
    const tableBody = document.getElementById('spc-cluster-table-body');
    const subcases = cachedSubcases || await fetchSubcases();
    const subcase = subcases.find(subcase => subcase.id == subcaseDropdown.value);

    // Clear the table before appending new rows
    tableBody.innerHTML = '';


    const fragment = document.createDocumentFragment();

    data.forEach(spcCluster => {
        const force = spcCluster.subcase_id2summed_forces[subcase.id] || [0, 0, 0, 0, 0, 0];

        // Generate the row content, including the copy button
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${spcCluster.id}</td>
            <td>
                <!-- Placeholder for the copy button -->
                <div class="spc-ids-cell"></div>
            </td>
            <td>${force[0].toFixed(3)}</td>
            <td>${force[1].toFixed(3)}</td>
            <td>${force[2].toFixed(3)}</td>
            <td>${calculateForceMagnitude(force).linear}</td>
            <td>${force[3].toFixed(3)}</td>
            <td>${force[4].toFixed(3)}</td>
            <td>${force[5].toFixed(3)}</td>
            <td>${calculateForceMagnitude(force).moment}</td>
        `;

        // Add the copy button to the second cell
        const spcIdsCell = row.querySelector('.spc-ids-cell');
        const spcIdsCopyButton = createCopyButton(spcCluster.spc_ids.split(",").join(", "), 'Copy SPC Nodes');
        spcIdsCell.appendChild(spcIdsCopyButton);

        // Append the row to the fragment
        fragment.appendChild(row);
    });

    // Append the fragment to the table body
    tableBody.appendChild(fragment);

    
}

function sortTableById() {
    // Toggle sorting direction
    sortDirection *= -1;

    // Sort the global data array
    spcclusters.sort((a, b) => (a.id - b.id) * sortDirection);

    // Re-render the table with sorted data
    renderTable(spcclusters);

    // Update the sorting icon
    const sortIcon = document.getElementById('id-sort-icon');
    if (sortDirection === 1) {
        sortIcon.textContent = '▲'; // Ascending
    } else {
        sortIcon.textContent = '▼'; // Descending
    }
}

// Attach sorting functionality to the ID column header
document.addEventListener('DOMContentLoaded', async () => {
    const idHeader = document.querySelector('th[data-sort="id"]');
    if (idHeader) {
        idHeader.addEventListener('click', sortTableById);
    }
    await fetchSubcases();
    await fetchSPCCluster();
});

