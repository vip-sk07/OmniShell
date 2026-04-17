import os
import os
if os.environ.get("RENDER"):
    import eventlet
    eventlet.monkey_patch()

import shlex
import shutil
import tempfile
from functools import wraps
from flask import Flask, request, jsonify, Response, render_template, session, redirect, url_for, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import func
from flask_socketio import SocketIO, emit

from translator import translate_command
from models import db, User, CommandHistory

app = Flask(__name__)
# Configurations
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-12345")

# Database Configuration (PostgreSQL for Cloud, SQLite for Local)
database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    # Fix for SQLAlchemy 1.4+ which requires 'postgresql://' instead of 'postgres://'
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///terminal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
if os.environ.get("RENDER"):
    from sqlalchemy.pool import NullPool
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "poolclass": NullPool,
    }
else:
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

db.init_app(app)

# --- Global Database Reset (One-time) ---
with app.app_context():
    # This will ensure the 'user' table is gone and 'app_users' is created fresh
    db.drop_all()
    db.create_all()

# --- Security Shims ---
# Smart Async Mode Detection
# (Render uses eventlet for performance; Local Parrot OS uses threading to avoid 'GreenSocket' crashes)
async_mode = 'eventlet' if os.environ.get("RENDER") else 'threading'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode=async_mode)

ALLOWED_COMMANDS = {
    # existing commands
    "ls", "pwd", "cat", "echo", "apt", "apt-get", "dnf", "yum", "pacman", "apk", "zypper", 
    "dpkg", "rpm", "clear", "whoami", "date", "cd", "sudo", "find", "df", "du", "mount", "sl",
    # newly added commands
    "systemctl", "service", "rc-service", "rc-update", "sv", "chkconfig",
    "ufw", "firewall-cmd", "iptables", "nft",
    "useradd", "adduser", "usermod", "userdel", "groupadd", "deluser", "addgroup", "passwd",
    "ip", "ifconfig", "ss", "netstat", "route",
    "journalctl", "tail", "dmesg", "grep",
    "apt-mark", "apt-cache", "dnf-automatic", "add-apt-repository", "apt-add-repository",
    # Part 2 expansion commands
    "free", "vmstat", "smem", "slabtop", "lscpu", "lshw", "lspci", "lsusb", "dmidecode",
    "fdisk", "lsblk", "blkid", "mkfs.ext4", "fsck", "parted", 
    "ps", "kill", "killall", "nice", "renice", "pgrep", "pkill",
    "tar", "zip", "unzip", "gzip", "bzip2",
    "ping", "traceroute", "dig", "nslookup", "curl", "wget", "nmap",
    "ssh", "scp", "rsync",
    "crontab", "at", 
    "env", "export", "alias", "source", "which", "type", 
    "chmod", "chown", "chgrp", "umask", "stat",
    "history"
}

# --- Connection Management ---
# Map user_id to active agent socket sid
active_agents = {}
# Store the OS footprint of the agent
agent_footprints = {}

# --- WebSocket Broker ---
@socketio.on('connect')
def wss_connect(auth=None):
    print(f"[Agent] Attempting connection to Cloud Platform via Websockets...")
    # Agent Auth
    if auth and 'token' in auth:
        token = auth['token']
        user = User.query.filter_by(api_token=token).first()
        if not user:
            print(f"[WSS Debug] AUTH FAILED: No user found for token starting with {token[:8]}")
            return False 
        active_agents[user.id] = request.sid
        print(f"[WSS Debug] SUCCESS: Agent connected for {user.username}")
        return True
    
    # Browser Auth
    if 'user_id' in session:
        print(f"[WSS Debug] SUCCESS: Browser connected for session user {session['user_id']}")
        return True
        
    print("[WSS Debug] AUTH FAILED: Unidentified connection rejected")
    return False

@socketio.on('disconnect')
def wss_disconnect():
    for user_id, sid in list(active_agents.items()):
        if sid == request.sid:
            del active_agents[user_id]
            if user_id in agent_footprints:
                del agent_footprints[user_id]
            # Tell browser
            emit('agent_status', {'status': 'disconnected'}, broadcast=True)

@socketio.on('agent_ready')
def on_agent_ready(os_info):
    for user_id, sid in active_agents.items():
        if sid == request.sid:
            agent_footprints[user_id] = os_info
            emit('agent_status', {'status': 'connected', 'info': os_info}, broadcast=True)
            break

@socketio.on('check_agent_status')
def check_agent_status():
    if 'user_id' not in session: return
    user_id = session['user_id']
    if user_id in active_agents and user_id in agent_footprints:
        emit('agent_status', {'status': 'connected', 'info': agent_footprints[user_id]})
    else:
        emit('agent_status', {'status': 'disconnected'})

# 1. BROWSER sends a command
@socketio.on('browser_command')
def handle_browser_command(data):
    if 'user_id' not in session: return
    user_id = session['user_id']
    
    command = data.get('command', '').strip()
    if not command:
        return

    agent_sid = active_agents.get(user_id)
    if not agent_sid:
        emit('command_output', {'output': '\r\n\x1b[31;1m[System Error] Client Runner Agent is disconnected.\r\nPlease open a fresh terminal and run [sudo python3 agent.py --token=YOUR_TOKEN]\x1b[0m\n'})
        return
        
    # Log command history locally on server
    new_history = CommandHistory(user_id=user_id, command_string=command)
    db.session.add(new_history)
    db.session.commit()
    
    if command == "history":
        histories = CommandHistory.query.filter_by(user_id=user_id).order_by(CommandHistory.timestamp.asc()).all()
        if not histories:
            emit('command_output', {'output': 'No history found.\r\n'})
        for idx, h in enumerate(histories, 1):
            emit('command_output', {'output': f"  {idx}  {h.command_string}\r\n"})
        return
        
    # Translate command using Agent's OS footprint
    os_info = agent_footprints.get(user_id, {})
    pkg = os_info.get('package_manager', 'apt')
    init_sys = os_info.get('init_system', 'systemd')
    translated = translate_command(command, pkg, init_sys)
    
    # Forward directly to the user's specific Agent connected socket
    emit('run_command', {'command': translated}, to=agent_sid)

# 1.2 BROWSER sends raw input
@socketio.on('browser_input')
def handle_browser_input(data):
    if 'user_id' not in session: return
    agent_sid = active_agents.get(session['user_id'])
    if agent_sid:
        emit('browser_input', data, to=agent_sid)
    else:
        # If no agent is connected, reflect output back to terminal to avoid "dead" feel
        emit('command_output', {'output': '\r\n\x1b[31m[System] No Agent Connected. Please run the local handshake command.\x1b[0m\r\n'})

# 1.3 BROWSER sends resize
@socketio.on('resize_terminal')
def handle_resize_terminal(data):
    if 'user_id' not in session: return
    agent_sid = active_agents.get(session['user_id'])
    if agent_sid:
        emit('resize_terminal', data, to=agent_sid)

# 1.5 BROWSER sends interrupt
@socketio.on('browser_interrupt')
def handle_browser_interrupt():
    if 'user_id' not in session: return
    agent_sid = active_agents.get(session['user_id'])
    if agent_sid:
        emit('interrupt_command', to=agent_sid)

# 2. AGENT sends output chunk
@socketio.on('command_output')
def on_command_output(data):
    emit('terminal_output', data, broadcast=True)

# 3. AGENT signals done
@socketio.on('command_done')
def on_command_done():
    emit('command_finished', broadcast=True)

# 4. AGENT signals CWD change
@socketio.on('cwd_changed')
def on_cwd_changed(data):
    emit('update_cwd', data, broadcast=True)

# --- Authentication Decorators ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def api_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"status": "error", "message": "unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

# --- Auth Routes ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('setup'))
        return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template('register.html', error="Username already exists. Please choose another or login.")
        
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        print(f"[Auth Debug] New user registered: {username}")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- Main App Routes ---
@app.route('/')
@login_required
def index():
    user = db.session.get(User, session.get('user_id'))
    if not user:
        session.clear()
        return redirect(url_for('login'))
    return render_template('index.html', username=user.username, api_token=user.api_token)

@app.route('/setup')
@login_required
def setup():
    user = db.session.get(User, session.get('user_id'))
    if not user:
        session.clear()
        return redirect(url_for('login'))
    return render_template('setup.html', username=user.username, api_token=user.api_token)

@app.route('/download_agent')
@login_required
def download_agent():
    # Create a temporary directory to build the zip
    with tempfile.TemporaryDirectory() as tmpdir:
        agent_src = os.path.join(os.path.dirname(__file__), 'universal_terminal_agent')
        install_script = os.path.join(os.path.dirname(__file__), 'install.sh')
        pyproject = os.path.join(os.path.dirname(__file__), 'pyproject.toml')
        
        # Target folder in zip
        zip_root = os.path.join(tmpdir, 'universal_terminal_agent_suite')
        os.makedirs(zip_root)
        
        # Copy package folder
        shutil.copytree(agent_src, os.path.join(zip_root, 'universal_terminal_agent'))
        # Copy root scripts
        shutil.copy2(install_script, zip_root)
        shutil.copy2(pyproject, zip_root)
        
        # Create zip
        zip_path = shutil.make_archive(os.path.join(tmpdir, 'universal_agent'), 'zip', zip_root)
        
        return send_file(zip_path, as_attachment=True, download_name='universal_agent_suite.zip')

@app.route('/download_installer')
@login_required
def download_installer():
    install_script = os.path.join(os.path.dirname(__file__), 'install.sh')
    return send_file(install_script, as_attachment=True, download_name='install.sh')

@app.route('/cwd', methods=['GET'])
@api_login_required
def cwd():
    return jsonify({"cwd": "~", "user": session.get('username')})

@app.route('/api/v1/history', methods=['GET'])
@api_login_required
def api_history():
    histories = CommandHistory.query.filter_by(user_id=session['user_id']).order_by(CommandHistory.timestamp.desc()).limit(100).all()
    results = [{"id": h.id, "command": h.command_string, "timestamp": h.timestamp.isoformat()} for h in histories]
    return jsonify({"status": "success", "history": results})

@app.route('/analytics')
@login_required
def analytics():
    top_commands = db.session.query(
        CommandHistory.command_string, 
        func.count(CommandHistory.id).label('count')
    ).filter_by(user_id=session['user_id']).group_by(CommandHistory.command_string).order_by(func.count(CommandHistory.id).desc()).limit(10).all()
    
    total_commands = CommandHistory.query.filter_by(user_id=session['user_id']).count()
    
    return render_template('analytics.html', 
                           username=session.get('username'), 
                           top_commands=top_commands,
                           total_commands=total_commands)


if __name__ == '__main__':
    with app.app_context():
        # One-time reset to ensure clean state
        db.drop_all()
        db.create_all()
    
    port = int(os.environ.get("PORT", 5050))
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    socketio.run(app, host='0.0.0.0', port=port, debug=debug_mode, allow_unsafe_werkzeug=True)
