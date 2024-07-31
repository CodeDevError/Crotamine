// js/screen.js
export const showMainContent = (loadingScreen, mainContent, currentScreen) => {
    setTimeout(() => {
        loadingScreen.style.display = 'none';
        mainContent.style.display = 'flex';
        document.querySelector(`[data-screen="${currentScreen}"]`).click();
    }, 5000);
};
