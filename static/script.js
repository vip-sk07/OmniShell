document.addEventListener('DOMContentLoaded', () => {
    const terminalBody = document.getElementById('terminal-body');
    const osInfoElem = document.getElementById('os-info');
    const xtermContainer = document.getElementById('xterm-container');
    const cmdInputContainer = document.querySelector('.command-line');
    
    // Hide our old manual input field, PTY handles it now
    if (cmdInputContainer) cmdInputContainer.style.display = 'none';

    let currentUser = "user";
    let currentHost = "linux";
    
    // Initialize xterm.js
    const term = new Terminal({
        theme: {
            background: '#0f111a',
            foreground: '#a9b1d6',
            cursor: '#a9b1d6',
            black: '#32344a',
            red: '#f7768e',
            green: '#9ece6a',
            yellow: '#e0af68',
            blue: '#7aa2f7',
            magenta: '#ad8ee6',
            cyan: '#449dab',
            white: '#787c99',
            brightBlack: '#444b6a',
            brightRed: '#ff7a93',
            brightGreen: '#b9f27c',
            brightYellow: '#ff9e64',
            brightBlue: '#7da6ff',
            brightMagenta: '#bb9af7',
            brightCyan: '#0db9d7',
            brightWhite: '#acb0d0'
        },
        fontFamily: "'Fira Code', monospace",
        fontSize: 15,
        cursorBlink: true,
        disableStdin: false // ENABLE STDIN
    });
    
    const fitAddon = new FitAddon.FitAddon();
    term.loadAddon(fitAddon);
    term.open(xtermContainer);
    fitAddon.fit();
    
    // WebSockets Setup
    const socket = io();

    // Send real-time input to server
    term.onData(data => {
        socket.emit('browser_input', { input: data });
    });

    // Handle resize
    term.onResize(size => {
        socket.emit('resize_terminal', { cols: size.cols, rows: size.rows });
    });

    window.addEventListener('resize', () => {
        fitAddon.fit();
    });

    socket.on('agent_status', (data) => {
        if (data.status === 'connected') {
            const osName = data.info.name || "Unknown Linux";
            const pkgMgr = data.info.package_manager || "apt";
            currentHost = data.info.id || 'linux';
            osInfoElem.innerHTML = `Agent Connection: [ <span style="color: #9ece6a;">ONLINE</span> ] | OS: <span style="color: #0db9d7;">${osName}</span> | Native Manager: <span style="color: #ff007c;">${pkgMgr}</span>`;
            
            // Sync terminal size once connected
            socket.emit('resize_terminal', { cols: term.cols, rows: term.rows });
        } else {
            osInfoElem.innerHTML = `Agent Connection: [ <span style="color: #f7768e;">OFFLINE</span> ] — Awaiting Runner Connection.`;
            currentHost = 'cloud';
        }
    });

    // Check on load
    socket.emit('check_agent_status');
    
    socket.on('terminal_output', (data) => {
        term.write(data.output);
    });

    socket.on('command_finished', () => {
        // In PTY mode, command_finished is rare (usually shell is always open)
    });
});
