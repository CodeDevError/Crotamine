// js/menu.js
export const setupMenuItems = (menuItems, screens) => {
    menuItems.forEach(item => {
        item.addEventListener('click', () => {
            menuItems.forEach(i => i.classList.remove('active'));
            item.classList.add('active');

            const targetScreen = item.getAttribute('data-screen');
            localStorage.setItem('currentScreen', targetScreen);
            screens.forEach(screen => {
                if (screen.id === targetScreen) {
                    screen.classList.add('active');
                } else {
                    screen.classList.remove('active');
                }
            });
        });

        item.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                item.click();
            }
        });
    });
};
