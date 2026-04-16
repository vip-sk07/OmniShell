#!/bin/bash

# Professional Installer for Universal Terminal Agent
# Targets: Parrot OS, Kali Linux, Debian, Ubuntu

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}==============================================${NC}"
echo -e "${BLUE}   Universal Terminal Agent: Professional Installer${NC}"
echo -e "${BLUE}==============================================${NC}"

# 1. Capture Source Directory (Before any 'cd')
SOURCE_DIR=$(dirname "$(readlink -f "$0")")

# 1.2 Verify all project files are present
REQUIRED_FILES=("universal_terminal_agent" "pyproject.toml")
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -e "$SOURCE_DIR/$file" ]; then
        echo -e "${RED}[Error] Missing required file: $file${NC}"
        echo -e "${RED}Please ensure you copied the entire project folder, not just the script!${NC}"
        echo -e "${RED}Tip: Use the 'Download Agent Suite' button on your dashboard to get a complete package.${NC}"
        exit 1
    fi
done

# 1.5 Check for Sudo
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}[Error] Please run this script with sudo privileges.${NC}"
  exit 1
fi

# 2. Check and Install System Dependencies
echo -e "${BLUE}[1/5] Checking system prerequisites...${NC}"

# Function to check if Python venv and pip are actually working
check_deps() {
    python3 -m venv --help > /dev/null 2>&1 && command -v pip3 > /dev/null 2>&1
}

if check_deps; then
    echo -e "${GREEN}Prerequisites already satisfied. Skipping system updates.${NC}"
else
    echo -e "${BLUE}Missing dependencies found. Attempting to install (requires internet)...${NC}"
    # Make update non-fatal. If it fails, maybe the cache is already good enough for install.
    apt-get update -qq || echo -e "${RED}Warning: apt update failed. Checking internet connection...${NC}"
    
    if ! apt-get install -y python3-pip python3-venv python3-full build-essential > /dev/null; then
        echo -e "${RED}[Error] Failed to install system dependencies.${NC}"
        echo -e "${RED}Your machine is reporting: 'Failed to fetch' error.${NC}"
        echo -e "${RED}Please check your internet connection or run 'sudo apt update' manually to fix your mirrors.${NC}"
        exit 1
    fi
fi

# 3. Create Sandbox Directory
INSTALL_DIR="/opt/universal-terminal-agent"
echo -e "${BLUE}[2/5] Creating environment in $INSTALL_DIR...${NC}"

if [ -d "$INSTALL_DIR" ]; then
    echo -e "Cleaning up old installation..."
    rm -rf "$INSTALL_DIR"
fi

mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# 4. Setup Virtual Environment
echo -e "${BLUE}[3/5] Setting up Python Sandbox...${NC}"
python3 -m venv venv
source venv/bin/activate

# 5. Copy Build Files
echo -e "${BLUE}[4/5] Copying application files...${NC}"
cp -r "$SOURCE_DIR/universal_terminal_agent" .
cp "$SOURCE_DIR/pyproject.toml" .
[ -f "$SOURCE_DIR/README.md" ] && cp "$SOURCE_DIR/README.md" . || echo "Skipping optional README.md"

# Install the package locally inside the VENV
echo -e "${BLUE}[5/5] Finalizing installation...${NC}"
./venv/bin/pip install . > /dev/null

# Link the binaries to system path
ln -sf "$INSTALL_DIR/venv/bin/universal-agent" /usr/local/bin/universal-agent
ln -sf "$INSTALL_DIR/venv/bin/universal-shim" /usr/local/bin/universal-shim

echo -e "${GREEN}==============================================${NC}"
echo -e "${GREEN}SUCCESS: Universal Terminal Agent is installed!${NC}"
echo -e "You can now run: ${BLUE}universal-agent --token=YOUR_TOKEN${NC}"
echo -e "From any terminal window."
echo -e "${GREEN}==============================================${NC}"
