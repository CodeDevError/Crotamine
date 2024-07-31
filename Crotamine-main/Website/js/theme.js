// js/theme.js
export const changeTheme = (theme) => {
    document.body.className = ''; // Clear existing theme classes
    document.body.classList.add(theme);
    document.querySelector('.menu').className = 'menu'; // Clear existing theme classes
    document.querySelector('.menu').classList.add(theme);
    localStorage.setItem('theme', theme);

    // Toggle between stylesheets
    if (theme === 'dark') {
        document.getElementById('dark-theme').disabled = false;
        document.getElementById('light-theme').disabled = true;
    } else {
        document.getElementById('dark-theme').disabled = true;
        document.getElementById('light-theme').disabled = false;
    }

    // Update table headers and cells for the selected theme
    const tableHeaders = document.querySelectorAll('table th');
    const tableCells = document.querySelectorAll('table td');
    tableHeaders.forEach(header => {
        header.className = ''; // Clear existing theme classes
        header.classList.add(theme);
    });
    tableCells.forEach(cell => {
        cell.className = ''; // Clear existing theme classes
        cell.classList.add(theme);
    });

    // Apply theme-specific styles to other elements
    document.querySelectorAll('.menu li').forEach(item => {
        item.className = ''; // Clear existing theme classes
        item.classList.add(theme);
    });
    document.querySelectorAll('.logout-button').forEach(button => {
        button.className = 'logout-button'; // Clear existing theme classes
        button.classList.add(theme);
    });
    document.querySelectorAll('.small-box button').forEach(button => {
        button.className = ''; // Clear existing theme classes
        button.classList.add(theme);
    });
    document.querySelectorAll('table').forEach(table => {
        table.className = ''; // Clear existing theme classes
        table.classList.add(theme);
    });
};
