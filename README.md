# Universal Linux Terminal: Enterprise Suite 🚀

A distributed, secure, and cross-distribution terminal emulator that allows you to control multiple Linux machines from a single web dashboard with automatic command translation.

🌐 **Live Demo / Public Access**: [https://omnishell.onrender.com/](https://omnishell.onrender.com/)

## 🏗️ Architecture
- **Web Dashboard (Server)**: A Flask-SocketIO broker that routes commands and displays real-time output.
- **Remote Runner (Agent)**: A Python-based agent that connects securely via WebSockets and manages a Pseudo-Terminal (PTY) session.

---

## 🛠️ Installation & Setup

### 1. Start the Server (The "Cloud" side)
Open a terminal in the project root and run:
```bash
sudo pip3 install -r requirements.txt
sudo python3 app.py
```
View the dashboard at `http://localhost:5050`.

### 2. Install the Agent (The "Laptop" side)
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
Go back to your browser. You can now type any Linux command (even from other distros) and it will be translated and executed in real-time.

---

## ✨ Features
- **PTY Bridge**: Supports interactive apps like `vim`, `nano`, and `top`.
- **Universal Translation**: Type `pacman` commands on Debian; it works automatically.
- **Analytical Dashboard**: Track command history and usage frequency.
- **Secure Handshake**: 256-bit encrypted API token authentication.
