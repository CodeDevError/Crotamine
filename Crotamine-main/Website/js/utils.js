// utils.js
export const validateInput = (input) => {
    const pattern = /^[a-zA-Z0-9_]+$/; // Alphanumeric and underscores only
    return pattern.test(input);
};
