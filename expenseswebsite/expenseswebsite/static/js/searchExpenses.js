// Get DOM elements
const searchField = document.querySelector("#searchField");
const tableOutput = document.querySelector('.table-output');
const appTable = document.querySelector('.app-table');
const tableBody = document.querySelector('.table-body');
const paginationContainer = document.querySelector('.pagination-container');
tableOutput.style.display = 'none';

// Event listener for search field
searchField.addEventListener('keyup', (e) => {
    const searchValue = e.target.value;

    if (searchValue.trim().length > 0) {
        // Hide pagination and clear table body
        paginationContainer.style.display = "none";
        tableBody.innerHTML = "";

        // Fetch search results from server
        fetch("/search-expenses", {
            body: JSON.stringify({ searchText: searchValue }),
            method: "POST",
        })
        .then((res) => res.json())
        .then((data) => {
            console.log("data", data);

            // Hide original table and show search results container
            appTable.style.display = "none";
            tableOutput.style.display = "block";

            if (data.length === 0) {
                tableOutput.innerHTML = "No search results found!";
            } else {
                // Generate HTML for each search result item
                const tableRows = data.map(item => `
                    <tr>
                        <td>${item.amount}</td>
                        <td>${item.category}</td>
                        <td>${item.description}</td>
                        <td>${item.date}</td>
                    </tr>
                `).join('');

                // Append generated HTML to table body
                tableBody.innerHTML = tableRows;
            }
        });
    } else {
        // Show original table and pagination
        tableOutput.style.display = "none";
        appTable.style.display = "block";
        paginationContainer.style.display = "block";
    }
});
