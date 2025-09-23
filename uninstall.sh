#!/bin/bash

# TempFox Uninstallation Script with UV Support
# Fighting-type Pokemon functions for system operations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Installation directories
INSTALL_DIR="$HOME/.local/share/tempfox"
BIN_DIR="$HOME/.local/bin"
TEMPFOX_BIN="$BIN_DIR/tempfox"

# Fighting-type Pokemon functions for system operations
# Hitmonlee: System verification - uses powerful kicks to check installation status
hitmonlee_verify_installation() {
    echo -e "${BLUE}🥋 Hitmonlee is checking TempFox installation with High Jump Kick...${NC}"
    
    if [ ! -d "$INSTALL_DIR" ] && [ ! -f "$TEMPFOX_BIN" ]; then
        echo -e "${YELLOW}⚠️  TempFox doesn't appear to be installed.${NC}"
        exit 0
    fi
    
    echo -e "${GREEN}✅ TempFox installation found${NC}"
}

# Primeape: Cleanup operations - uses rage to forcefully remove files
primeape_remove_installation() {
    echo -e "${BLUE}😡 Primeape is removing TempFox installation with Rage...${NC}"
    
    # Remove installation directory
    if [ -d "$INSTALL_DIR" ]; then
        echo -e "${YELLOW}🗑️  Removing installation directory: $INSTALL_DIR${NC}"
        rm -rf "$INSTALL_DIR"
    fi
    
    # Remove binary
    if [ -f "$TEMPFOX_BIN" ]; then
        echo -e "${YELLOW}🗑️  Removing binary: $TEMPFOX_BIN${NC}"
        rm -f "$TEMPFOX_BIN"
    fi
    
    echo -e "${GREEN}✅ TempFox files removed${NC}"
}

# Machamp: Shell configuration cleanup - uses four arms to clean multiple configs
machamp_cleanup_shell() {
    echo -e "${BLUE}🔧 Machamp is cleaning shell configuration with Dynamic Punch...${NC}"
    
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
            echo -e "${YELLOW}⚠️  Unknown shell: $SHELL_NAME. Please remove $BIN_DIR from your PATH manually.${NC}"
            return
            ;;
    esac
    
    # Remove TempFox PATH entry from shell config
    if [ -f "$RC_FILE" ]; then
        # Create backup
        cp "$RC_FILE" "$RC_FILE.tempfox.backup"
        
        # Remove TempFox-related lines
        sed -i.tmp '/# TempFox installation/d' "$RC_FILE"
        sed -i.tmp "\|export PATH=\"$BIN_DIR:\$PATH\"|d" "$RC_FILE"
        rm -f "$RC_FILE.tmp"
        
        echo -e "${GREEN}✅ Cleaned shell configuration in $RC_FILE${NC}"
        echo -e "${BLUE}ℹ️  Backup saved as $RC_FILE.tempfox.backup${NC}"
    fi
}

# Machoke: Directory cleanup - uses powerful muscles to clean empty directories
machoke_cleanup_directories() {
    echo -e "${BLUE}💪 Machoke is cleaning empty directories with Strength...${NC}"
    
    # Remove empty parent directories if they exist and are empty
    if [ -d "$HOME/.local/share" ]; then
        rmdir "$HOME/.local/share" 2>/dev/null || true
    fi
    
    if [ -d "$HOME/.local/bin" ] && [ -z "$(ls -A "$HOME/.local/bin")" ]; then
        rmdir "$HOME/.local/bin" 2>/dev/null || true
        echo -e "${GREEN}✅ Removed empty bin directory${NC}"
    fi
    
    if [ -d "$HOME/.local" ] && [ -z "$(ls -A "$HOME/.local")" ]; then
        rmdir "$HOME/.local" 2>/dev/null || true
        echo -e "${GREEN}✅ Removed empty .local directory${NC}"
    fi
}

# Hitmonchan: User feedback - uses punching combinations to deliver messages
hitmonchan_show_success() {
    echo -e "${BLUE}👊 Hitmonchan delivers the final message with Thunder Punch...${NC}"
    echo ""
    echo -e "${GREEN}🎉 TempFox uninstallation completed successfully!${NC}"
    echo ""
    echo -e "${YELLOW}📋 Final steps:${NC}"
    echo -e "   1. Restart your terminal or run: ${BLUE}source ~/.${SHELL_NAME}rc${NC}"
    echo -e "   2. Verify removal: ${BLUE}which tempfox${NC} (should return nothing)"
    echo ""
    echo -e "${BLUE}🔗 Thank you for using TempFox!${NC}"
    echo ""
}

# Main uninstallation process
main() {
    echo -e "${GREEN}🦊 TempFox Uninstallation Script${NC}"
    echo -e "${BLUE}Using Fighting-type Pokemon for system operations!${NC}"
    echo ""
    
    # Confirm uninstallation
    echo -e "${YELLOW}⚠️  This will completely remove TempFox from your system.${NC}"
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}ℹ️  Uninstallation cancelled.${NC}"
        exit 0
    fi
    
    hitmonlee_verify_installation
    primeape_remove_installation
    machamp_cleanup_shell
    machoke_cleanup_directories
    hitmonchan_show_success
}

# Run main function
main "$@"
