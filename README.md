# OmniShell Cloud: Distributed Enterprise Terminal 🚀

OmniShell Cloud is a distributed, secure, and cross-distribution terminal emulator that allows you to control multiple Linux machines from a single beautiful web dashboard with automatic command translation.

🌐 **Live Demo / Public Access**: [https://omnishell.onrender.com/](https://omnishell.onrender.com/)

## 🏗️ Architecture
- **Web Dashboard (Broker)**: A Flask-SocketIO server that routes commands, tracks command history analytics, and displays real-time execution output.
- **Remote Runner (Agent)**: A Python-based agent that connects securely via WebSockets and manages a Pseudo-Terminal (PTY) session, translating commands transparently.

---

## 🛠️ Installation & Setup

### 1. Start the Server (The "Cloud" side)
Open a terminal in the project root and run:
```bash
pip3 install -r requirements.txt
python3 app.py
```
View the dashboard at `http://localhost:5050`.

### 2. Install the Agent (The "Local" side)
You can install the agent on any number of remote Linux machines using our professional one-line installer:
```bash
sudo bash install.sh
```
*This handles everything: creating a virtual environment, installing dependencies, and linking the command globally.*

---

## 🚀 Usage

### Step 1: Get your Token
Log in to the Web Dashboard. You will see a unique **API Token** assigned to your account.

### Step 2: Connect your Runner
On the machine you want to control, run:
```bash
universal-agent --token=YOUR_TOKEN --url=http://your-server-ip:5050
```

### Step 3: Start Controlling!
Go back to your browser. You can now type any Linux command (e.g., `dnf install vim` on an Ubuntu machine) and it will be translated and executed in real-time.

---

## ✨ Features
- **Interactive PTY Bridge**: Supports fully interactive terminal apps like `vim`, `nano`, and `htop` right from the browser.
- **Universal Translation Engine**: Type commands from any package manager (`apt`, `dnf`, `pacman`, `zypper`, `apk`), and it automatically executes the correct native command.
- **Analytical Dashboard**: Track your command history, usage frequency, and system details.
- **Secure Handshake**: Ensures security with API token-based authentication.
