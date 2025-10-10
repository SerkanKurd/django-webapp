window.addEventListener('DOMContentLoaded', event => {
    // Simple-DataTables
    // https://github.com/fiduswriter/Simple-DataTables/wiki

    // Select all tables with the 'datatable-init' class
    const datatables = document.querySelectorAll('.datatable-init');
    datatables.forEach(datatable => {
        new simpleDatatables.DataTable(datatable);
    });

});
