// commands.js

// Define the valid commands directly in JavaScript
const validCommands = {
    'help': [],
    'start': ['<input>'],
    'stop': [],
    'status': [],
    'restart': ['<input>'],
    'connect': ['<input'],
    'list': [],
    'tasklist': [],
    'screenshare': []
};

export const validateCommand = (command) => {
    const [baseCommand, ...args] = command.split(' ');
    if (!validCommands.hasOwnProperty(baseCommand)) {
        alert(`Invalid command: ${baseCommand}`);
        return false;
    }
    if (validCommands[baseCommand].includes('<input>') && args.length === 0) {
        alert(`Command ${baseCommand} requires additional input`);
        return false;
    }
    return true;
};

export const getValidCommands = () => {
    return validCommands;
};
