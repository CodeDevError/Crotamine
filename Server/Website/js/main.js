import { checkAuth, promptLogin, hashPassword } from './auth.js';
import { setCookie, deleteCookie } from './cookies.js';
import { loadPreferences } from './preferences.js';
import { setupMenuItems } from './menu.js';
import { showMainContent } from './screen.js';
import { setupCommandInput } from './input.js';
import { changeTheme } from './theme.js';

document.addEventListener("DOMContentLoaded", async () => {
    console.log("DOMContentLoaded event fired.");
    const menuItems = document.querySelectorAll('.menu li');
    const screens = document.querySelectorAll('.screen');
    const inputCommand = document.getElementById('input-command');
    const mainContent = document.getElementById('main-content');
    const loadingScreen = document.getElementById('loading-screen');
    let loginAttempts = 0;
    const MAX_ATTEMPTS = 5;

    // Check authentication
    console.log("Starting authentication check...");
    const authenticated = await checkAuth(() => promptLogin(loginAttempts, MAX_ATTEMPTS, setCookie, hashPassword));
    console.log("Authentication result:", authenticated);
    if (!authenticated) {
        console.log("Authentication failed. Exiting script.");
        return;
    }

    // Load preferences
    console.log("Loading preferences...");
    const { currentScreen, currentTheme } = loadPreferences();

    // Apply the current theme
    changeTheme(currentTheme);

    // Show main content after loading
    console.log("Showing main content...");
    showMainContent(loadingScreen, mainContent, currentScreen);

    // Setup menu items
    console.log("Setting up menu items...");
    setupMenuItems(menuItems, screens);

    // Setup command input
    console.log("Setting up command input...");
    const socket = io();
    setupCommandInput(inputCommand, socket);

    // Handle incoming server messages
    socket.on('server-message', (data) => {
        const serverOutput = document.getElementById('server-output');
        serverOutput.innerHTML += `<p>[*] ${data.message}</p>`;
    });

    // Setup theme change buttons
    document.querySelector('.theme-option.dark').addEventListener('click', () => changeTheme('dark'));
    document.querySelector('.theme-option.white').addEventListener('click', () => changeTheme('white'));
});
