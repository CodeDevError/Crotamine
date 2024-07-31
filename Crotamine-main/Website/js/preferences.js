// js/preferences.js
import { changeTheme } from './theme.js';

export const loadPreferences = () => {
    const currentScreen = localStorage.getItem('currentScreen') || 'dashboard';
    const currentTheme = localStorage.getItem('theme') || 'white';
    document.body.classList.add(currentTheme);
    document.querySelector('.menu').classList.add(currentTheme);
    changeTheme(currentTheme);
    return { currentScreen, currentTheme };
};
