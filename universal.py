import sys
import subprocess
import os

from translator import translate_command
from detector import detect_os

def main():
    if len(sys.argv) < 2:
        return

    # Reconstruct the command from arguments
    command = " ".join(sys.argv[1:])
    
    # Detect local OS
    os_info = detect_os()
    pkg = os_info.get("package_manager", "apt")
    init = os_info.get("init_system", "systemd")
    
    # Translate
    translated = translate_command(command, pkg, init)
    
    if translated != command:
        print(f"\033[1;33m[Universal Translation]\033[0m {translated}")
    
    # Run the real command
    # We use os.system or subprocess.call to inherit the shell environment
    try:
        subprocess.call(translated, shell=True)
    except Exception as e:
        print(f"\033[1;31m[Universal Error]\033[0m {str(e)}")

if __name__ == "__main__":
    main()
