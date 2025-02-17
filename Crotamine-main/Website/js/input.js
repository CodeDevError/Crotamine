// input.js
import { validateCommand } from './commands.js';

export const setupCommandInput = (inputCommand, socket) => {
    const sendCommand = () => {
        const command = inputCommand.value;
        console.log('Entered Command:', command); // Debug output to see the entered command
        if (validateCommand(command)) {
            socket.emit('client-command', { command }, (response) => {
                if (response.error) {
                    console.error('Error:', response.error);
                }
            });
            inputCommand.value = '';
        }
    };

    inputCommand.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendCommand();
        }
    });

    window.sendCommand = sendCommand; // Expose sendCommand function to global scope
};
