// js/auth.js
import { getCookie, deleteCookie, setCookie } from './cookies.js';
import { validateInput } from './utils.js';

export const hashPassword = async (password) => {
    const msgUint8 = new TextEncoder().encode(password); // encode as (utf-8) Uint8Array
    const hashBuffer = await crypto.subtle.digest('SHA-256', msgUint8); // hash the message
    const hashArray = Array.from(new Uint8Array(hashBuffer)); // convert buffer to byte array
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join(''); // convert bytes to hex string
    return hashHex;
};

export const generateJWT = (payload) => {
    const header = { alg: 'HS256', typ: 'JWT' };
    const base64Header = btoa(JSON.stringify(header));
    const base64Payload = btoa(JSON.stringify({ ...payload, exp: Math.floor(Date.now() / 1000) + 60 * 60 }));
    const signature = btoa('secret'); // Replace with a secure method to generate the signature
    return `${base64Header}.${base64Payload}.${signature}`;
};

export const checkAuth = async (promptLogin) => {
    console.log("Checking authentication...");
    const token = getCookie('jwt-token');
    console.log("Token from getCookie:", token);
    if (!token) {
        console.log("No token found. Prompting login.");
        await promptLogin();
        return false;
    } else {
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            console.log("Token payload:", payload);
            const isExpired = Date.now() >= payload.exp * 1000;
            console.log("Is token expired?", isExpired);
            if (isExpired) {
                console.log("Token expired. Prompting login.");
                deleteCookie('jwt-token');
                await promptLogin();
                return false;
            } else {
                console.log("Token is valid.");
                return true;
            }
        } catch (e) {
            console.log("Error parsing token. Prompting login.", e);
            deleteCookie('jwt-token');
            await promptLogin();
            return false;
        }
    }
};

export const promptLogin = async (loginAttempts, MAX_ATTEMPTS, setCookie, hashPassword) => {
    console.log("Prompting login...");
    if (loginAttempts >= MAX_ATTEMPTS) {
        alert('Too many login attempts. Please try again later.');
        return false;
    }

    const username = prompt('Enter username:');
    const password = prompt('Enter password:');
    if (username && password) {
        if (validateInput(username) && validateInput(password)) {
            const hashedPassword = await hashPassword(password);
            if (username === '1' && hashedPassword === await hashPassword('1')) {
                console.log("Login successful. Setting token.");
                const token = generateJWT({ username });
                setCookie('jwt-token', token, 1);
                console.log("Token set:", token);
                const newToken = getCookie('jwt-token');
                console.log("Token from cookie:", newToken);
                return true;
            } else {
                console.log("Invalid credentials.");
                alert('Invalid credentials');
                loginAttempts++;
                setTimeout(() => { loginAttempts = 0; }, 60000); // Reset attempts after 1 minute
                return await promptLogin(loginAttempts, MAX_ATTEMPTS, setCookie, hashPassword);
            }
        } else {
            console.log("Invalid input.");
            alert('Invalid input');
            return await promptLogin(loginAttempts, MAX_ATTEMPTS, setCookie, hashPassword);
        }
    }
    return false;
};
