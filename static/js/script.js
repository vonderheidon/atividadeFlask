document.addEventListener("DOMContentLoaded", function() {
    const deleteLinks = document.querySelectorAll(".delete-link");

    deleteLinks.forEach(link => {
        link.addEventListener("click", function(event) {
            const confirmDelete = confirm("Você tem certeza que deseja excluir este produto?");
            if (!confirmDelete) {
                event.preventDefault();
            }
        });
    });

    const searchBar = document.getElementById('searchBar');
    const productTable = document.getElementById('productTable');
    let productRows = Array.from(productTable.getElementsByTagName('tr'));

    let filteredRows = [...productRows];

    function updatePagination() {
        const rowsPerPage = 5;
        let currentPage = 1;

        const totalRows = filteredRows.length;
        const totalPages = Math.ceil(totalRows / rowsPerPage);

        if (totalRows === 0) {
            document.getElementById('pageDisplay').textContent = `Nenhum produto encontrado`;
            document.getElementById('prevPage').disabled = true;
            document.getElementById('nextPage').disabled = true;
            return;
        }

        function displayPage(page) {
            const startRow = (page - 1) * rowsPerPage;
            const endRow = startRow + rowsPerPage;

            filteredRows.forEach((row, index) => {
                if (index >= startRow && index < endRow) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });

            document.getElementById('pageDisplay').textContent = `Página ${page} de ${totalPages}`;
            document.getElementById('prevPage').disabled = page === 1;
            document.getElementById('nextPage').disabled = page === totalPages;
        }

        displayPage(currentPage);

        document.getElementById('prevPage').addEventListener('click', function() {
            if (currentPage > 1) {
                currentPage--;
                displayPage(currentPage);
            }
        });

        document.getElementById('nextPage').addEventListener('click', function() {
            if (currentPage < totalPages) {
                currentPage++;
                displayPage(currentPage);
            }
        });
    }

    searchBar.addEventListener('keyup', function(event) {
        const searchTerm = event.target.value.toLowerCase();

        filteredRows = productRows.filter(row => {
            const productName = row.querySelector('.product-name') ? row.querySelector('.product-name').textContent.toLowerCase() : '';
            const isVisible = productName.includes(searchTerm);
            row.style.display = isVisible ? '' : 'none';
            return isVisible;
        });

        updatePagination();
    });
    updatePagination();
});

document.addEventListener('keydown', function(event) {
    if (event.ctrlKey && event.shiftKey && event.key === 'R') {
        event.preventDefault();
        var hiddenDiv = document.getElementById('hiddenDiv');
        hiddenDiv.classList.remove('hidden');
    }
});
