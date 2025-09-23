# TempFox Installation Script for Windows with UV Support
# Fighting-type Pokemon functions for system operations

param(
    [switch]$Force
)

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"

# Installation directories
$InstallDir = "$env:LOCALAPPDATA\tempfox"
$BinDir = "$env:LOCALAPPDATA\tempfox\bin"

# Fighting-type Pokemon functions for system operations
# Hitmonlee: System verification - uses powerful kicks to check system status
function Invoke-HitmonleeVerifyPython {
    Write-Host "🥋 Hitmonlee is checking Python installation with High Jump Kick..." -ForegroundColor $Blue
    
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Python not found"
        }
        
        $versionMatch = $pythonVersion -match "Python (\d+)\.(\d+)"
        if ($versionMatch) {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            
            if ($major -ge 3 -and $minor -ge 8) {
                Write-Host "✅ Python $($matches[1]).$($matches[2]) detected (>= 3.8)" -ForegroundColor $Green
            } else {
                throw "Python version too old: $($matches[1]).$($matches[2])"
            }
        } else {
            throw "Could not parse Python version"
        }
    }
    catch {
        Write-Host "❌ Python 3.8 or higher is required. Please install Python from https://python.org" -ForegroundColor $Red
        exit 1
    }
}

# Machoke: Environment setup - uses powerful muscles to build environments
function Invoke-MachokeSetupUV {
    Write-Host "💪 Machoke is setting up UV with Strength..." -ForegroundColor $Blue
    
    try {
        uv --version | Out-Null
        Write-Host "✅ UV is already installed" -ForegroundColor $Green
    }
    catch {
        Write-Host "📦 Installing UV package manager..." -ForegroundColor $Yellow
        
        try {
            # Install UV using the official installer
            Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
            
            # Refresh environment variables
            $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "User") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "Machine")
            
            uv --version | Out-Null
            Write-Host "✅ UV installed successfully" -ForegroundColor $Green
        }
        catch {
            Write-Host "❌ UV installation failed. Please install UV manually from https://github.com/astral-sh/uv" -ForegroundColor $Red
            exit 1
        }
    }
}

# Machamp: System configuration - uses four arms to configure multiple aspects
function Invoke-MachampConfigureEnvironment {
    Write-Host "🔧 Machamp is configuring the environment with Dynamic Punch..." -ForegroundColor $Blue
    
    # Create installation directories
    if (Test-Path $InstallDir) {
        if ($Force) {
            Remove-Item $InstallDir -Recurse -Force
        } else {
            Write-Host "⚠️  Installation directory already exists. Use -Force to overwrite." -ForegroundColor $Yellow
            exit 1
        }
    }
    
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    New-Item -ItemType Directory -Path $BinDir -Force | Out-Null
    
    # Create virtual environment with UV
    Write-Host "🔨 Creating virtual environment..." -ForegroundColor $Yellow
    Set-Location $InstallDir
    uv venv tempfox-env
    
    # Install TempFox
    Write-Host "📦 Installing TempFox with UV..." -ForegroundColor $Yellow
    & "$InstallDir\tempfox-env\Scripts\activate.ps1"
    uv pip install tempfox
    
    # Create wrapper script
    $wrapperScript = @"
@echo off
call "$InstallDir\tempfox-env\Scripts\activate.bat"
python -m tempfox %*
"@
    
    $wrapperScript | Out-File -FilePath "$BinDir\tempfox.bat" -Encoding ASCII
    
    Write-Host "✅ TempFox installed successfully" -ForegroundColor $Green
}

# Primeape: Shell configuration - uses rage to forcefully update environment
function Invoke-PrimeapeConfigureEnvironment {
    Write-Host "😡 Primeape is updating environment variables with Rage..." -ForegroundColor $Blue
    
    # Get current user PATH
    $currentPath = [System.Environment]::GetEnvironmentVariable("PATH", "User")
    
    # Add bin directory to PATH if not already present
    if ($currentPath -notlike "*$BinDir*") {
        $newPath = "$BinDir;$currentPath"
        [System.Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
        $env:PATH = "$BinDir;$env:PATH"
        Write-Host "✅ Added $BinDir to user PATH" -ForegroundColor $Green
    } else {
        Write-Host "ℹ️  PATH already configured" -ForegroundColor $Yellow
    }
}

# Hitmonchan: User feedback - uses punching combinations to deliver messages
function Invoke-HitmonchanShowSuccess {
    Write-Host "👊 Hitmonchan delivers the final message with Thunder Punch..." -ForegroundColor $Blue
    Write-Host ""
    Write-Host "🎉 TempFox installation completed successfully!" -ForegroundColor $Green
    Write-Host ""
    Write-Host "📋 Next steps:" -ForegroundColor $Yellow
    Write-Host "   1. Restart your PowerShell session or terminal"
    Write-Host "   2. Test the installation: " -NoNewline; Write-Host "tempfox --help" -ForegroundColor $Blue
    Write-Host "   3. Start using TempFox: " -NoNewline; Write-Host "tempfox" -ForegroundColor $Blue
    Write-Host ""
    Write-Host "🔗 For more information, visit: " -NoNewline; Write-Host "https://github.com/alfdav/tempfox" -ForegroundColor $Blue
    Write-Host ""
}

# Main installation process
function Main {
    Write-Host "🦊 TempFox Installation Script for Windows" -ForegroundColor $Green
    Write-Host "Using Fighting-type Pokemon for system operations!" -ForegroundColor $Blue
    Write-Host ""
    
    Invoke-HitmonleeVerifyPython
    Invoke-MachokeSetupUV
    Invoke-MachampConfigureEnvironment
    Invoke-PrimeapeConfigureEnvironment
    Invoke-HitmonchanShowSuccess
}

# Run main function
try {
    Main
}
catch {
    Write-Host "❌ Installation failed: $($_.Exception.Message)" -ForegroundColor $Red
    exit 1
}
