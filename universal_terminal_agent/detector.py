import os

def detect_init_system():
    """Detect the running init system."""
    if os.path.exists("/run/systemd/private") or os.path.isdir("/run/systemd"):
        return "systemd"
    if os.path.exists("/run/openrc") or os.path.exists("/sbin/rc-service"):
        return "openrc"
    if os.path.exists("/run/runit") or os.path.exists("/usr/bin/sv"):
        return "runit"
    if os.path.exists("/etc/init.d"):
        return "sysv"
    return "systemd"

def detect_os():
    """Detect the Linux distribution and its package manager."""
    os_info = {
        "name": "Unknown Linux",
        "id": "unknown",
        "id_like": "",
        "package_manager": "unknown"
    }
    
    # Try reading /etc/os-release
    try:
        if os.path.exists('/etc/os-release'):
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    if '=' in line:
                        key, value = line.split('=', 1)
                        # Remove quotes
                        value = value.strip('"\'')
                        
                        if key == "NAME":
                            os_info["name"] = value
                        elif key == "ID":
                            os_info["id"] = value
                        elif key == "ID_LIKE":
                            os_info["id_like"] = value
                            
    except Exception as e:
        print(f"Error reading /etc/os-release: {e}")
        
    # Determine package manager based on ID or ID_LIKE
    distro_id = os_info["id"].lower()
    id_like = os_info["id_like"].lower()
    
    if "debian" in id_like or "ubuntu" in id_like or distro_id in ["debian", "ubuntu", "kali", "parrot", "linuxmint", "pop"]:
        os_info["package_manager"] = "apt"
    elif "rhel" in id_like or "fedora" in id_like or "centos" in id_like or distro_id in ["fedora", "rhel", "centos", "rocky", "almalinux"]:
        os_info["package_manager"] = "dnf"
    elif "arch" in id_like or distro_id in ["arch", "manjaro", "endeavouros"]:
        os_info["package_manager"] = "pacman"
    elif "suse" in id_like or distro_id in ["opensuse", "sles"]:
        os_info["package_manager"] = "zypper"
    elif "alpine" in distro_id:
        os_info["package_manager"] = "apk"
    
    os_info["init_system"] = detect_init_system()
        
    return os_info

if __name__ == "__main__":
    print(detect_os())
