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

# Hitmonlee: Go verification - uses Close Combat to check Go installation
hitmonlee_verify_go() {
    echo -e "${BLUE}🥋 Hitmonlee is checking Go installation with Close Combat...${NC}"
    
    if command -v go &> /dev/null; then
        GO_VERSION=$(go version | awk '{print $3}')
        echo -e "${GREEN}✅ Go is installed: ${GO_VERSION}${NC}"
        return 0
    fi
    
    echo -e "${YELLOW}⚠️  Go is not installed. Installing Go...${NC}"
    
    # Detect platform
    OS=$(uname -s | tr '[:upper:]' '[:lower:]')
    ARCH=$(uname -m)
    
    case $ARCH in
        x86_64) ARCH="amd64" ;;
        aarch64|arm64) ARCH="arm64" ;;
        armv6l) ARCH="armv6l" ;;
        armv7l) ARCH="armv6l" ;;
        *) echo -e "${RED}❌ Unsupported architecture: $ARCH${NC}"; exit 1 ;;
    esac
    
    # Use Go 1.21.5 (stable version)
    GO_VERSION="1.21.5"
    GO_FILENAME="go${GO_VERSION}.${OS}-${ARCH}.tar.gz"
    GO_URL="https://go.dev/dl/${GO_FILENAME}"
    GO_INSTALL_DIR="$HOME/.local/go"
    
    echo -e "${YELLOW}📦 Downloading Go ${GO_VERSION} for ${OS}-${ARCH}...${NC}"
    
    # Create installation directory
    mkdir -p "$GO_INSTALL_DIR"
    
    # Download and extract Go
    if command -v curl &> /dev/null; then
        curl -L "$GO_URL" | tar -xz -C "$GO_INSTALL_DIR" --strip-components=1
    elif command -v wget &> /dev/null; then
        wget -O- "$GO_URL" | tar -xz -C "$GO_INSTALL_DIR" --strip-components=1
    else
        echo -e "${RED}❌ Neither curl nor wget is available. Please install one of them.${NC}"
        exit 1
    fi
    
    # Add Go to PATH for current session
    export PATH="$GO_INSTALL_DIR/bin:$PATH"
    
    if command -v go &> /dev/null; then
        echo -e "${GREEN}✅ Go installed successfully${NC}"
    else
        echo -e "${RED}❌ Go installation failed${NC}"
        exit 1
    fi
}

# Hitmonlee: CloudFox verification - uses Mega Kick to check CloudFox installation
hitmonlee_verify_cloudfox() {
    echo -e "${BLUE}🥋 Hitmonlee is checking CloudFox installation with Mega Kick...${NC}"
    
    if command -v cloudfox &> /dev/null; then
        echo -e "${GREEN}✅ CloudFox is already installed${NC}"
        return 0
    fi
    
    echo -e "${YELLOW}⚠️  CloudFox is not installed. Installing CloudFox...${NC}"
    
    # Ensure Go is available
    if ! command -v go &> /dev/null; then
        echo -e "${RED}❌ Go is required for CloudFox installation but not found${NC}"
        exit 1
    fi
    
    # Install CloudFox using go install
    echo -e "${YELLOW}📦 Installing CloudFox from source...${NC}"
    if go install "github.com/BishopFox/cloudfox@latest"; then
        # Add GOPATH/bin to PATH if needed
        GOPATH=${GOPATH:-"$HOME/go"}
        GOBIN="$GOPATH/bin"
        
        if [[ ":$PATH:" != *":$GOBIN:"* ]]; then
            export PATH="$GOBIN:$PATH"
        fi
        
        if command -v cloudfox &> /dev/null; then
            echo -e "${GREEN}✅ CloudFox installed successfully${NC}"
        else
            echo -e "${RED}❌ CloudFox installation failed - binary not found in PATH${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ CloudFox installation failed${NC}"
        exit 1
    fi
}

# Machoke: Environment setup - uses powerful muscles to build environments
machoke_setup_uv() {
    echo -e "${BLUE}💪 Machoke is setting up UV with Strength...${NC}"
    
    if command -v uv &> /dev/null; then
        UV_VERSION=$(uv --version 2>/dev/null || echo "unknown")
        echo -e "${GREEN}✅ UV is already installed: ${UV_VERSION}${NC}"
        return 0
    fi
    
    echo -e "${YELLOW}📦 UV not found. Installing UV package manager...${NC}"
    
    # Try multiple installation methods
    if command -v curl &> /dev/null; then
        echo -e "${YELLOW}🔄 Installing UV using curl...${NC}"
        if curl -LsSf https://astral.sh/uv/install.sh | sh; then
            echo -e "${GREEN}✅ UV installed successfully via curl${NC}"
        else
            echo -e "${RED}❌ UV installation via curl failed${NC}"
            exit 1
        fi
    elif command -v wget &> /dev/null; then
        echo -e "${YELLOW}🔄 Installing UV using wget...${NC}"
        if wget -qO- https://astral.sh/uv/install.sh | sh; then
            echo -e "${GREEN}✅ UV installed successfully via wget${NC}"
        else
            echo -e "${RED}❌ UV installation via wget failed${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ Neither curl nor wget is available. Cannot install UV automatically.${NC}"
        echo -e "${YELLOW}Please install curl or wget, then run this script again.${NC}"
        echo -e "${YELLOW}Or install UV manually from: https://github.com/astral-sh/uv${NC}"
        exit 1
    fi
    
    # Add UV to PATH for current session
    export PATH="$HOME/.cargo/bin:$PATH"
    
    # Verify UV installation
    if command -v uv &> /dev/null; then
        UV_VERSION=$(uv --version 2>/dev/null || echo "unknown")
        echo -e "${GREEN}✅ UV is ready for use: ${UV_VERSION}${NC}"
    else
        echo -e "${RED}❌ UV installation failed. UV binary not found in PATH.${NC}"
        echo -e "${YELLOW}💡 Try restarting your terminal or manually adding ~/.cargo/bin to your PATH${NC}"
        exit 1
    fi
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
            echo -e "${YELLOW}⚠️  Unknown shell: $SHELL_NAME. Please add paths to your PATH manually.${NC}"
            return
            ;;
    esac
    
    # Paths to add
    GO_BIN_DIR="$HOME/.local/go/bin"
    GOPATH_BIN_DIR="$HOME/go/bin"
    UV_BIN_DIR="$HOME/.cargo/bin"
    
    # Add TempFox bin directory to PATH if not already present
    if ! grep -q "$BIN_DIR" "$RC_FILE" 2>/dev/null; then
        echo "" >> "$RC_FILE"
        echo "# TempFox installation" >> "$RC_FILE"
        echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$RC_FILE"
        echo -e "${GREEN}✅ Added $BIN_DIR to PATH in $RC_FILE${NC}"
    else
        echo -e "${YELLOW}ℹ️  TempFox PATH already configured in $RC_FILE${NC}"
    fi
    
    # Add Go bin directory to PATH if Go was installed locally
    if [[ -d "$GO_BIN_DIR" ]] && ! grep -q "$GO_BIN_DIR" "$RC_FILE" 2>/dev/null; then
        echo "# Go installation" >> "$RC_FILE"
        echo "export PATH=\"$GO_BIN_DIR:\$PATH\"" >> "$RC_FILE"
        echo -e "${GREEN}✅ Added $GO_BIN_DIR to PATH in $RC_FILE${NC}"
    fi
    
    # Add UV bin directory to PATH if UV was installed
    if [[ -d "$UV_BIN_DIR" ]] && ! grep -q "$UV_BIN_DIR" "$RC_FILE" 2>/dev/null; then
        echo "# UV package manager" >> "$RC_FILE"
        echo "export PATH=\"$UV_BIN_DIR:\$PATH\"" >> "$RC_FILE"
        echo -e "${GREEN}✅ Added $UV_BIN_DIR to PATH in $RC_FILE${NC}"
    fi
    
    # Add GOPATH bin directory to PATH for CloudFox
    if ! grep -q "GOPATH.*bin" "$RC_FILE" 2>/dev/null; then
        echo "# Go workspace" >> "$RC_FILE"
        echo "export GOPATH=\"\$HOME/go\"" >> "$RC_FILE"
        echo "export PATH=\"\$GOPATH/bin:\$PATH\"" >> "$RC_FILE"
        echo -e "${GREEN}✅ Added GOPATH/bin to PATH in $RC_FILE${NC}"
    fi
    
    # Update current session PATH
    export PATH="$BIN_DIR:$GO_BIN_DIR:$GOPATH_BIN_DIR:$UV_BIN_DIR:$PATH"
    export GOPATH="$HOME/go"
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
    hitmonlee_verify_go
    hitmonlee_verify_cloudfox
    machoke_setup_uv
    machamp_configure_environment
    primeape_configure_shell
    hitmonchan_show_success
}

# Run main function
main "$@"
