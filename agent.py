import argparse
import socketio
import os
import pty
import select
import subprocess
import termios
import struct
import fcntl
import shlex
import sys
import threading
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from detector import detect_os

sio = socketio.Client()
SERVER_URL = "http://localhost:5050"
# Master FD for the PTY
fd = None
child_pid = None

def read_from_pty():
    global fd
    while True:
        if fd:
            try:
                # Wait for data to be available
                ready, _, _ = select.select([fd], [], [], 0.1)
                if ready:
                    data = os.read(fd, 1024)
                    if not data:
                        break
                    if sio.connected:
                        sio.emit('command_output', {'output': data.decode('utf-8', errors='ignore')})
            except (OSError, ValueError):
                break
        else:
            time.sleep(0.1)

@sio.event
def connect():
    print(f"[Agent] Successfully authenticated and connected to {SERVER_URL}!")
    os_info = detect_os()
    sio.emit('agent_ready', os_info)

@sio.event
def disconnect():
    print("[Agent] Connection to server lost.")

@sio.on('run_command')
def on_run_command(data):
    """
    In the new PTY model, we don't 'run' and 'wait'. 
    We just inject the translated command into the existing PTY shell.
    """
    global fd
    command = data.get('command', '').strip()
    if command and fd:
        # Inject the command into the PTY
        os.write(fd, (command + "\n").encode())

@sio.on('browser_input')
def on_browser_input(data):
    global fd
    input_data = data.get('input', '')
    if fd and input_data:
        os.write(fd, input_data.encode())

@sio.on('resize_terminal')
def on_resize(data):
    global fd
    cols = data.get('cols', 80)
    rows = data.get('rows', 24)
    if fd:
        # Set the terminal size of the PTY slave
        size = struct.pack("HHHH", rows, cols, 0, 0)
        fcntl.ioctl(fd, termios.TIOCSWINSZ, size)

@sio.on('interrupt_command')
def on_interrupt():
    global fd
    if fd:
        # Send Ctrl+C (ETX) to the PTY
        os.write(fd, b'\x03')

def start_pty(token):
    global fd, child_pid
    # Fork a new process with a PTY
    child_pid, fd = pty.fork()
    
    if child_pid == 0:
        # Child process
        # Start a login shell
        shell = os.environ.get('SHELL', '/bin/bash')
        os.execlp(shell, shell, "-l")
    else:
        # Parent process: Start the reading thread
        threading.Thread(target=read_from_pty, daemon=True).start()
        
        # Give the shell a moment to show the first prompt
        time.sleep(0.5)
        
        # Inject Universal Shims (Aliases)
        # We point them to the universal.py script
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "universal.py"))
        
        # List of commands to hijack for translation
        foreign_cmds = ["apt", "dnf", "yum", "pacman", "zypper", "apk", "ufw", "systemctl"]
        
        # The 'sudo ' alias (with space) is a magic Linux trick that tells bash 
        # to check the NEXT word for aliases too! This fixes 'sudo dnf' translation.
        alias_cmd = "alias sudo='sudo '; "
        for cmd in foreign_cmds:
            alias_cmd += f"alias {cmd}='python3 \"{script_path}\" {cmd}'; "
        
        # Hidden injection (leading space prevents it from appearing in history on most shells)
        os.write(fd, f" {alias_cmd} \n".encode())
        # Clear the line visually if needed
        os.write(fd, b"\r")

def main():
    parser = argparse.ArgumentParser(description="Terminal Secure Client Runner (PTY Mode)")
    parser.add_argument("--token", required=True, help="Your User API Connection Token")
    parser.add_argument("--url", default="http://localhost:5050", help="Web Dashboard URL")
    args = parser.parse_args()
    
    global SERVER_URL
    SERVER_URL = args.url

    # Start the local shell session
    start_pty(args.token)

    print(f"[Agent] Connecting to Cloud Platform {SERVER_URL} via Websockets...")
    try:
        sio.connect(SERVER_URL, auth={'token': args.token})
        sio.wait()
    except KeyboardInterrupt:
        print("\n[Agent] Stopping and disconnecting...")
        sio.disconnect()
        sys.exit(0)
    except Exception as e:
        print(f"[Error] Failed to connect: {e}")

if __name__ == "__main__":
    main()
