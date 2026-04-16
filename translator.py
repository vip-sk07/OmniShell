# Base mappings
MAPPINGS = {
    # Package management
    "apt install": {
        "apt": "apt-get install -y",
        "dnf": "dnf install -y",
        "pacman": "pacman -S --noconfirm",
        "zypper": "zypper install -y",
        "apk": "apk add --no-interactive"
    },
    "apt remove": {
        "apt": "apt-get remove -y",
        "dnf": "dnf remove -y",
        "pacman": "pacman -R --noconfirm",
        "zypper": "zypper remove -y",
        "apk": "apk del"
    },
    "apt update": {
        "apt": "apt-get update",
        "dnf": "dnf check-update",
        "pacman": "pacman -Sy",
        "zypper": "zypper refresh",
        "apk": "apk update"
    },
    "apt upgrade": {
        "apt": "apt-get upgrade -y",
        "dnf": "dnf upgrade -y", 
        "pacman": "pacman -Su --noconfirm",
        "zypper": "zypper update -y",
        "apk": "apk upgrade --no-interactive"
    },
    "apt search": {
        "apt": "apt-cache search",
        "dnf": "dnf search",
        "pacman": "pacman -Ss",
        "zypper": "zypper search",
        "apk": "apk search"
    },
    "dpkg -l": {
        "apt": "dpkg -l",
        "dnf": "rpm -qa",
        "pacman": "pacman -Q",
        "zypper": "rpm -qa",
        "apk": "apk info"
    },
    "pacman -Syu": {
        "apt": "apt-get update && apt-get upgrade -y",
        "dnf": "dnf upgrade --refresh -y",
        "pacman": "pacman -Syu --noconfirm",
        "zypper": "zypper dup -y",
        "apk": "apk update && apk upgrade --no-interactive"
    },
    # ISSUE-16
    "apt autoremove": {
        "apt": "apt-get autoremove -y",
        "dnf": "dnf autoremove -y",
        "pacman": "pacman -Rns $(pacman -Qdtq) --noconfirm",
        "zypper": "zypper packages --unneeded",
        "apk": "apk autoremove"
    },
    "apt autoclean": {
        "apt": "apt-get autoclean",
        "dnf": "dnf clean packages",
        "pacman": "pacman -Sc --noconfirm",
        "zypper": "zypper clean",
        "apk": "apk cache clean"
    },
    "apt clean": {
        "apt": "apt-get clean",
        "dnf": "dnf clean all",
        "pacman": "pacman -Scc --noconfirm",
        "zypper": "zypper clean --all",
        "apk": "apk cache clean"
    },
    # ISSUE-17
    "apt show": {
        "apt": "apt-cache show",
        "dnf": "dnf info",
        "pacman": "pacman -Si",
        "zypper": "zypper info",
        "apk": "apk info -a"
    },
    "dpkg -s": {
        "apt": "dpkg -s",
        "dnf": "rpm -qi",
        "pacman": "pacman -Qi",
        "zypper": "rpm -qi",
        "apk": "apk info -a"
    },
    # ISSUE-18
    "apt-mark hold": {
        "apt": "apt-mark hold",
        "dnf": "dnf versionlock add",
        "pacman": "# pacman has no hold; edit /etc/pacman.conf IgnorePkg",
        "zypper": "zypper addlock",
        "apk": "apk add -u --no-self-upgrade"
    },
    "apt-mark unhold": {
        "apt": "apt-mark unhold",
        "dnf": "dnf versionlock delete",
        "pacman": "# remove from IgnorePkg in /etc/pacman.conf",
        "zypper": "zypper removelock",
        "apk": "# apk does not support package locks"
    },
    # ISSUE-19
    "dpkg --verify": {
        "apt": "dpkg --verify",
        "dnf": "rpm -V",
        "pacman": "pacman -Qk",
        "zypper": "rpm -V",
        "apk": "apk verify"
    },
    # ISSUE-20 (Services - depends on init system)
    "systemctl start": {
        "systemd": "systemctl start",
        "openrc": "rc-service",
        "runit": "sv start",
        "sysv": "service"
    },
    "systemctl stop": {
        "systemd": "systemctl stop",
        "openrc": "rc-service",
        "runit": "sv stop",
        "sysv": "service"
    },
    "systemctl restart": {
        "systemd": "systemctl restart",
        "openrc": "rc-service",
        "runit": "sv restart",
        "sysv": "service"
    },
    "systemctl status": {
        "systemd": "systemctl status",
        "openrc": "rc-service",
        "runit": "sv status",
        "sysv": "service"
    },
    "systemctl enable": {
        "systemd": "systemctl enable",
        "openrc": "rc-update add",
        "runit": "# create symlink in /var/service/",
        "sysv": "chkconfig --add"
    },
    "systemctl disable": {
        "systemd": "systemctl disable",
        "openrc": "rc-update del",
        "runit": "# remove symlink from /var/service/",
        "sysv": "chkconfig --del"
    },
    "systemctl is-enabled": {
        "systemd": "systemctl is-enabled",
        "openrc": "rc-update show",
        "runit": "ls /var/service/",
        "sysv": "chkconfig --list"
    },
    # ISSUE-21
    "ufw enable": {
        "apt": "ufw enable",
        "dnf": "systemctl enable --now firewalld",
        "pacman": "systemctl enable --now iptables",
        "zypper": "systemctl enable --now firewalld",
        "apk": "rc-update add iptables"
    },
    "ufw status": {
        "apt": "ufw status verbose",
        "dnf": "firewall-cmd --state",
        "pacman": "iptables -L -n -v",
        "zypper": "firewall-cmd --state",
        "apk": "iptables -L -n -v"
    },
    "ufw allow": {
        "apt": "ufw allow",
        "dnf": "firewall-cmd --permanent --add-port",
        "pacman": "iptables -A INPUT -p tcp --dport",
        "zypper": "firewall-cmd --permanent --add-port",
        "apk": "iptables -A INPUT -p tcp --dport"
    },
    "ufw deny": {
        "apt": "ufw deny",
        "dnf": "firewall-cmd --permanent --remove-port",
        "pacman": "iptables -D INPUT -p tcp --dport",
        "zypper": "firewall-cmd --permanent --remove-port",
        "apk": "iptables -D INPUT -p tcp --dport"
    },
    # ISSUE-22
    "adduser": {
        "apt": "adduser",
        "dnf": "useradd -m",
        "pacman": "useradd -m",
        "zypper": "useradd -m",
        "apk": "adduser"
    },
    "deluser": {
        "apt": "deluser",
        "dnf": "userdel -r",
        "pacman": "userdel -r",
        "zypper": "userdel -r",
        "apk": "deluser"
    },
    "addgroup": {
        "apt": "addgroup",
        "dnf": "groupadd",
        "pacman": "groupadd",
        "zypper": "groupadd",
        "apk": "addgroup"
    },
    "usermod -aG": {
        "apt": "usermod -aG",
        "dnf": "usermod -aG",
        "pacman": "usermod -aG",
        "zypper": "usermod -aG",
        "apk": "adduser"
    },
    # ISSUE-23
    "ip addr": {
        "apt": "ip addr",
        "dnf": "ip addr",
        "pacman": "ip addr",
        "zypper": "ip addr",
        "apk": "ip addr"
    },
    "ifconfig": {
        "apt": "ip addr",
        "dnf": "ip addr",
        "pacman": "ip addr",
        "zypper": "ip addr",
        "apk": "ifconfig"
    },
    "ss -tuln": {
        "apt": "ss -tuln",
        "dnf": "ss -tuln",
        "pacman": "ss -tuln",
        "zypper": "ss -tuln",
        "apk": "netstat -tuln"
    },
    "netstat -tuln": {
        "apt": "ss -tuln",
        "dnf": "ss -tuln",
        "pacman": "ss -tuln",
        "zypper": "ss -tuln",
        "apk": "netstat -tuln"
    },
    "ip route": {
        "apt": "ip route",
        "dnf": "ip route",
        "pacman": "ip route",
        "zypper": "ip route",
        "apk": "ip route"
    },
    # ISSUE-24
    "journalctl -u": {
        "apt": "journalctl -u",
        "dnf": "journalctl -u",
        "pacman": "journalctl -u",
        "zypper": "journalctl -u",
        "apk": "tail -f /var/log/messages"
    },
    "journalctl -f": {
        "apt": "journalctl -f",
        "dnf": "journalctl -f",
        "pacman": "journalctl -f",
        "zypper": "journalctl -f",
        "apk": "tail -f /var/log/messages"
    },
    "journalctl -xe": {
        "apt": "journalctl -xe",
        "dnf": "journalctl -xe",
        "pacman": "journalctl -xe",
        "zypper": "journalctl -xe",
        "apk": "dmesg | tail -50"
    },
    "journalctl --since": {
        "apt": "journalctl --since",
        "dnf": "journalctl --since",
        "pacman": "journalctl --since",
        "zypper": "journalctl --since",
        "apk": "grep"
    },
    # ISSUE-26
    "add-apt-repository": {
        "apt": "add-apt-repository",
        "dnf": "dnf config-manager --add-repo",
        "pacman": "# edit /etc/pacman.conf to add repos manually",
        "zypper": "zypper addrepo",
        "apk": "# edit /etc/apk/repositories manually"
    }
}

ALIASES = {
    # Install
    "install": "apt install",
    "apt install": "apt install",
    "apt-get install": "apt install",
    "dnf install": "apt install",
    "yum install": "apt install",
    "pacman -S": "apt install",
    "zypper install": "apt install",
    "zypper in": "apt install",
    "apk add": "apt install",
    
    # Remove
    "remove": "apt remove",
    "uninstall": "apt remove",
    "apt remove": "apt remove",
    "apt-get remove": "apt remove",
    "dnf remove": "apt remove",
    "yum remove": "apt remove",
    "pacman -R": "apt remove",
    "zypper remove": "apt remove",
    "zypper rm": "apt remove",
    "apk del": "apt remove",
    
    # Update
    "update": "apt update",
    "apt update": "apt update",
    "apt-get update": "apt update",
    "dnf check-update": "apt update",
    "yum check-update": "apt update",
    "pacman -Sy": "apt update",
    "zypper refresh": "apt update",
    "zypper ref": "apt update",
    "apk update": "apt update",
    
    # Upgrade
    "upgrade": "apt upgrade",
    "apt upgrade": "apt upgrade",
    "apt-get upgrade": "apt upgrade",
    "dnf upgrade": "apt upgrade",
    "dnf update": "apt upgrade",
    "yum upgrade": "apt upgrade",
    "yum update": "apt upgrade",
    "pacman -Su": "apt upgrade",
    "pacman -Syu": "pacman -Syu",
    "zypper update": "apt upgrade",
    "zypper up": "apt upgrade",
    "apk upgrade": "apt upgrade",
    
    # Search
    "search": "apt search",
    "apt search": "apt search",
    "apt-cache search": "apt search",
    "dnf search": "apt search",
    "yum search": "apt search",
    "pacman -Ss": "apt search",
    "zypper search": "apt search",
    "zypper se": "apt search",
    "apk search": "apt search",

    # List
    "list": "dpkg -l",
    "dpkg -l": "dpkg -l",
    "rpm -qa": "dpkg -l",
    "pacman -Q": "dpkg -l",
    "apk info": "dpkg -l",
    
    # ISSUE-16
    "autoremove": "apt autoremove",
    "apt autoremove": "apt autoremove",
    "dnf autoremove": "apt autoremove",
    "pacman -Rns": "apt autoremove",
    "apk autoremove": "apt autoremove",
    "autoclean": "apt autoclean",
    "apt autoclean": "apt autoclean",
    "dnf clean": "apt autoclean",
    "pacman -Sc": "apt autoclean",
    "clean": "apt clean",
    "apt clean": "apt clean",
    "dnf clean all": "apt clean",
    "pacman -Scc": "apt clean",

    # ISSUE-17
    "apt show": "apt show",
    "apt-cache show": "apt show",
    "dnf info": "apt show",
    "yum info": "apt show",
    "pacman -Si": "apt show",
    "pacman -Qi": "dpkg -s",
    "zypper info": "apt show",
    "dpkg -s": "dpkg -s",
    "rpm -qi": "dpkg -s",

    # ISSUE-18
    "apt-mark hold": "apt-mark hold",
    "dnf versionlock add": "apt-mark hold",
    "zypper addlock": "apt-mark hold",
    "apt-mark unhold": "apt-mark unhold",
    "zypper removelock": "apt-mark unhold",

    # ISSUE-19
    "dpkg --verify": "dpkg --verify",
    "rpm -V": "dpkg --verify",
    "pacman -Qk": "dpkg --verify",
    "apk verify": "dpkg --verify",

    # ISSUE-20
    "systemctl start": "systemctl start",
    "service start": "systemctl start",
    "rc-service start": "systemctl start",
    "sv start": "systemctl start",
    "systemctl stop": "systemctl stop",
    "service stop": "systemctl stop",
    "systemctl restart": "systemctl restart",
    "service restart": "systemctl restart",
    "systemctl status": "systemctl status",
    "service status": "systemctl status",
    "systemctl enable": "systemctl enable",
    "rc-update add": "systemctl enable",
    "chkconfig --add": "systemctl enable",
    "systemctl disable": "systemctl disable",
    "rc-update del": "systemctl disable",

    # ISSUE-21
    "ufw enable": "ufw enable",
    "ufw status": "ufw status",
    "ufw allow": "ufw allow",
    "ufw deny": "ufw deny",
    "firewall-cmd --state": "ufw status",
    "firewall-cmd --add-port": "ufw allow",

    # ISSUE-22
    "adduser": "adduser",
    "useradd": "adduser",
    "useradd -m": "adduser",
    "deluser": "deluser",
    "userdel": "deluser",
    "userdel -r": "deluser",
    "addgroup": "addgroup",
    "groupadd": "addgroup",
    "usermod -aG": "usermod -aG",

    # ISSUE-23
    "ip addr": "ip addr",
    "ifconfig": "ifconfig",
    "ss": "ss -tuln",
    "ss -tuln": "ss -tuln",
    "netstat": "netstat -tuln",
    "netstat -tuln": "netstat -tuln",
    "ip route": "ip route",
    "route": "ip route",

    # ISSUE-24
    "journalctl -u": "journalctl -u",
    "journalctl -f": "journalctl -f",
    "journalctl -xe": "journalctl -xe",
    "journalctl --since": "journalctl --since",
    "journalctl": "journalctl -f",

    # ISSUE-26
    "add-apt-repository": "add-apt-repository",
    "apt-add-repository": "add-apt-repository",
    "dnf config-manager --add-repo": "add-apt-repository",
    "zypper addrepo": "add-apt-repository",
    "zypper ar": "add-apt-repository"
}

def translate_command(command, target_pkg_manager, target_init_system="systemd"):
    parts = command.strip().split()
    if not parts:
        return command
        
    is_sudo = False
    if parts[0] == "sudo":
        is_sudo = True
        parts = parts[1:]
        if not parts:
            return command
            
    cmd_base = ""
    rest = ""
    
    if len(parts) >= 2:
        potential_base = f"{parts[0]} {parts[1]}"
        if potential_base in ALIASES:
            cmd_base = potential_base
            rest = " ".join(parts[2:])
            
    if not cmd_base and parts[0] in ALIASES:
        cmd_base = parts[0]
        rest = " ".join(parts[1:])
        
    if cmd_base in ALIASES:
        canonical = ALIASES[cmd_base]
        
        # Check if it's a service command which relies on init system
        if canonical.startswith("systemctl"):
            translated_base = MAPPINGS.get(canonical, {}).get(target_init_system, canonical)
        else:
            translated_base = MAPPINGS.get(canonical, {}).get(target_pkg_manager, canonical)
            
        final_cmd = translated_base
        if rest:
            # Special logic for openrc reversed args (rc-service <name> <action>)
            if translated_base == "rc-service":
                action = cmd_base.split()[-1]
                final_cmd = f"rc-service {rest} {action}"
            else:
                final_cmd = f"{translated_base} {rest}".strip()
            
        if is_sudo:
            return f"sudo {final_cmd}"
        return final_cmd
        
    if is_sudo:
        return f"sudo {' '.join(parts)}"
    return command
