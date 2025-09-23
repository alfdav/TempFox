#!/bin/bash

# TempFox Installation Script with UV Support
# Fighting-type Pokemon functions for system operations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Installation directory
INSTALL_DIR="$HOME/.local/share/tempfox"
BIN_DIR="$HOME/.local/bin"

# Fighting-type Pokemon functions for system operations
# Hitmonlee: System verification - uses powerful kicks to check system status
hitmonlee_verify_python() {
    echo -e "${BLUE}🥋 Hitmonlee is checking Python installation with High Jump Kick...${NC}"
    
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.8 or higher.${NC}"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
    REQUIRED_VERSION="3.8"
    
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        echo -e "${GREEN}✅ Python ${PYTHON_VERSION} detected (>= ${REQUIRED_VERSION})${NC}"
    else
        echo -e "${RED}❌ Python ${PYTHON_VERSION} is too old. Please install Python ${REQUIRED_VERSION} or higher.${NC}"
        exit 1
    fi
}

# Machoke: Environment setup - uses powerful muscles to build environments
machoke_setup_uv() {
    echo -e "${BLUE}💪 Machoke is setting up UV with Strength...${NC}"
    
    if ! command -v uv &> /dev/null; then
        echo -e "${YELLOW}📦 Installing UV package manager...${NC}"
        curl -LsSf https://astral.sh/uv/install.sh | sh
        
        # Add UV to PATH for current session
        export PATH="$HOME/.cargo/bin:$PATH"
        
        if ! command -v uv &> /dev/null; then
            echo -e "${RED}❌ UV installation failed. Please install UV manually.${NC}"
            exit 1
        fi
    fi
    
    echo -e "${GREEN}✅ UV is ready for use${NC}"
}

# Machamp: System configuration - uses four arms to configure multiple aspects
machamp_configure_environment() {
    echo -e "${BLUE}🔧 Machamp is configuring the environment with Dynamic Punch...${NC}"
    
    # Create installation directory
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$BIN_DIR"
    
    # Create virtual environment with UV
    echo -e "${YELLOW}🔨 Creating virtual environment...${NC}"
    cd "$INSTALL_DIR"
    uv venv tempfox-env
    
    # Activate virtual environment and install TempFox
    echo -e "${YELLOW}📦 Installing TempFox with UV...${NC}"
    source tempfox-env/bin/activate
    uv pip install tempfox
    
    # Create wrapper script
    cat > "$BIN_DIR/tempfox" << 'EOF'
#!/bin/bash
source "$HOME/.local/share/tempfox/tempfox-env/bin/activate"
exec python -m tempfox "$@"
EOF
    
    chmod +x "$BIN_DIR/tempfox"
    
    echo -e "${GREEN}✅ TempFox installed successfully${NC}"
}

# Primeape: Shell configuration - uses rage to forcefully update shell configs
primeape_configure_shell() {
    echo -e "${BLUE}😡 Primeape is updating shell configuration with Rage...${NC}"
    
    # Detect shell
    SHELL_NAME=$(basename "$SHELL")
    
    case "$SHELL_NAME" in
        "bash")
            RC_FILE="$HOME/.bashrc"
            ;;
        "zsh")
            RC_FILE="$HOME/.zshrc"
            ;;
        *)
            echo -e "${YELLOW}⚠️  Unknown shell: $SHELL_NAME. Please add $BIN_DIR to your PATH manually.${NC}"
            return
            ;;
    esac
    
    # Add bin directory to PATH if not already present
    if ! grep -q "$BIN_DIR" "$RC_FILE" 2>/dev/null; then
        echo "" >> "$RC_FILE"
        echo "# TempFox installation" >> "$RC_FILE"
        echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$RC_FILE"
        echo -e "${GREEN}✅ Added $BIN_DIR to PATH in $RC_FILE${NC}"
    else
        echo -e "${YELLOW}ℹ️  PATH already configured in $RC_FILE${NC}"
    fi
    
    # Update current session PATH
    export PATH="$BIN_DIR:$PATH"
}

# Hitmonchan: User feedback - uses punching combinations to deliver messages
hitmonchan_show_success() {
    echo -e "${BLUE}👊 Hitmonchan delivers the final message with Thunder Punch...${NC}"
    echo ""
    echo -e "${GREEN}🎉 TempFox installation completed successfully!${NC}"
    echo ""
    echo -e "${YELLOW}📋 Next steps:${NC}"
    echo -e "   1. Restart your terminal or run: ${BLUE}source ~/.${SHELL_NAME}rc${NC}"
    echo -e "   2. Test the installation: ${BLUE}tempfox --help${NC}"
    echo -e "   3. Start using TempFox: ${BLUE}tempfox${NC}"
    echo ""
    echo -e "${BLUE}🔗 For more information, visit: https://github.com/alfdav/tempfox${NC}"
    echo ""
}

# Main installation process
main() {
    echo -e "${GREEN}🦊 TempFox Installation Script${NC}"
    echo -e "${BLUE}Using Fighting-type Pokemon for system operations!${NC}"
    echo ""
    
    hitmonlee_verify_python
    machoke_setup_uv
    machamp_configure_environment
    primeape_configure_shell
    hitmonchan_show_success
}

# Run main function
main "$@"
