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

# Hitmonlee: Go verification - uses Close Combat to check Go installation
function Invoke-HitmonleeVerifyGo {
    Write-Host "🥋 Hitmonlee is checking Go installation with Close Combat..." -ForegroundColor $Blue
    
    try {
        $goVersion = go version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Go is installed: $goVersion" -ForegroundColor $Green
            return
        }
    }
    catch {
        # Go not found, continue to installation
    }
    
    Write-Host "⚠️  Go is not installed. Installing Go..." -ForegroundColor $Yellow
    
    # Detect architecture
    $arch = if ([Environment]::Is64BitOperatingSystem) { "amd64" } else { "386" }
    
    # Use Go 1.21.5 (stable version)
    $goVersion = "1.21.5"
    $goFilename = "go$goVersion.windows-$arch.zip"
    $goUrl = "https://go.dev/dl/$goFilename"
    $goInstallDir = "$env:LOCALAPPDATA\go"
    
    Write-Host "📦 Downloading Go $goVersion for windows-$arch..." -ForegroundColor $Yellow
    
    try {
        # Create installation directory
        New-Item -ItemType Directory -Path $goInstallDir -Force | Out-Null
        
        # Download Go
        $tempFile = "$env:TEMP\$goFilename"
        Invoke-WebRequest -Uri $goUrl -OutFile $tempFile
        
        # Extract Go
        Write-Host "📂 Extracting Go..." -ForegroundColor $Yellow
        Expand-Archive -Path $tempFile -DestinationPath $goInstallDir -Force
        
        # Clean up
        Remove-Item $tempFile
        
        # Add Go to PATH for current session
        $goBinPath = "$goInstallDir\go\bin"
        $env:PATH = "$goBinPath;$env:PATH"
        
        # Verify installation
        $goVersion = go version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Go installed successfully" -ForegroundColor $Green
        } else {
            throw "Go installation verification failed"
        }
    }
    catch {
        Write-Host "❌ Go installation failed: $($_.Exception.Message)" -ForegroundColor $Red
        exit 1
    }
}

# Hitmonlee: CloudFox verification - uses Mega Kick to check CloudFox installation
function Invoke-HitmonleeVerifyCloudFox {
    Write-Host "🥋 Hitmonlee is checking CloudFox installation with Mega Kick..." -ForegroundColor $Blue
    
    try {
        cloudfox --help | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ CloudFox is already installed" -ForegroundColor $Green
            return
        }
    }
    catch {
        # CloudFox not found, continue to installation
    }
    
    Write-Host "⚠️  CloudFox is not installed. Installing CloudFox..." -ForegroundColor $Yellow
    
    # Ensure Go is available
    try {
        go version | Out-Null
        if ($LASTEXITCODE -ne 0) {
            throw "Go is required for CloudFox installation but not found"
        }
    }
    catch {
        Write-Host "❌ Go is required for CloudFox installation but not found" -ForegroundColor $Red
        exit 1
    }
    
    # Install CloudFox using go install
    Write-Host "📦 Installing CloudFox from source..." -ForegroundColor $Yellow
    try {
        go install github.com/BishopFox/cloudfox@latest
        
        # Add GOPATH/bin to PATH if needed
        $goPath = if ($env:GOPATH) { $env:GOPATH } else { "$env:USERPROFILE\go" }
        $goBin = "$goPath\bin"
        
        if ($env:PATH -notlike "*$goBin*") {
            $env:PATH = "$goBin;$env:PATH"
        }
        
        # Verify installation
        cloudfox --help | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ CloudFox installed successfully" -ForegroundColor $Green
        } else {
            throw "CloudFox installation verification failed - binary not found in PATH"
        }
    }
    catch {
        Write-Host "❌ CloudFox installation failed: $($_.Exception.Message)" -ForegroundColor $Red
        exit 1
    }
}

# Machoke: Environment setup - uses powerful muscles to build environments
function Invoke-MachokeSetupUV {
    Write-Host "💪 Machoke is setting up UV with Strength..." -ForegroundColor $Blue
    
    try {
        $uvVersion = uv --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ UV is already installed: $uvVersion" -ForegroundColor $Green
            return
        }
    }
    catch {
        # UV not found, continue to installation
    }
    
    Write-Host "📦 UV not found. Installing UV package manager..." -ForegroundColor $Yellow
    
    try {
        # Method 1: Try official PowerShell installer
        Write-Host "🔄 Installing UV using official PowerShell installer..." -ForegroundColor $Yellow
        try {
            Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
            Write-Host "✅ UV installed successfully via PowerShell installer" -ForegroundColor $Green
        }
        catch {
            Write-Host "⚠️  PowerShell installer failed, trying alternative method..." -ForegroundColor $Yellow
            
            # Method 2: Try direct download and install
            $uvVersion = "0.1.18"  # Use a known stable version
            $arch = if ([Environment]::Is64BitOperatingSystem) { "x86_64" } else { "i686" }
            $uvUrl = "https://github.com/astral-sh/uv/releases/download/$uvVersion/uv-$arch-pc-windows-msvc.zip"
            $uvInstallDir = "$env:LOCALAPPDATA\uv"
            
            Write-Host "📦 Downloading UV $uvVersion for windows-$arch..." -ForegroundColor $Yellow
            
            # Create installation directory
            New-Item -ItemType Directory -Path $uvInstallDir -Force | Out-Null
            
            # Download UV
            $tempFile = "$env:TEMP\uv.zip"
            Invoke-WebRequest -Uri $uvUrl -OutFile $tempFile
            
            # Extract UV
            Write-Host "📂 Extracting UV..." -ForegroundColor $Yellow
            Expand-Archive -Path $tempFile -DestinationPath $uvInstallDir -Force
            
            # Clean up
            Remove-Item $tempFile
            
            # Add UV to PATH for current session
            $uvBinPath = "$uvInstallDir"
            $env:PATH = "$uvBinPath;$env:PATH"
            
            Write-Host "✅ UV installed successfully via direct download" -ForegroundColor $Green
        }
        
        # Refresh environment variables
        $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "User") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "Machine")
        
        # Verify UV installation
        $uvVersion = uv --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ UV is ready for use: $uvVersion" -ForegroundColor $Green
        } else {
            throw "UV installation verification failed - binary not found in PATH"
        }
    }
    catch {
        Write-Host "❌ UV installation failed: $($_.Exception.Message)" -ForegroundColor $Red
        Write-Host "💡 Please try one of these alternatives:" -ForegroundColor $Yellow
        Write-Host "   1. Install UV manually from: https://github.com/astral-sh/uv" -ForegroundColor $Yellow
        Write-Host "   2. Use pip instead: pip install tempfox" -ForegroundColor $Yellow
        Write-Host "   3. Restart PowerShell as Administrator and try again" -ForegroundColor $Yellow
        exit 1
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
    $pathsToAdd = @()
    
    # Add TempFox bin directory to PATH if not already present
    if ($currentPath -notlike "*$BinDir*") {
        $pathsToAdd += $BinDir
        Write-Host "✅ Will add $BinDir to user PATH" -ForegroundColor $Green
    } else {
        Write-Host "ℹ️  TempFox PATH already configured" -ForegroundColor $Yellow
    }
    
    # Add Go bin directory to PATH if Go was installed locally
    $goBinDir = "$env:LOCALAPPDATA\go\go\bin"
    if ((Test-Path $goBinDir) -and ($currentPath -notlike "*$goBinDir*")) {
        $pathsToAdd += $goBinDir
        Write-Host "✅ Will add $goBinDir to user PATH" -ForegroundColor $Green
    }
    
    # Add UV bin directory to PATH if UV was installed
    $uvBinDir = "$env:LOCALAPPDATA\uv"
    if ((Test-Path $uvBinDir) -and ($currentPath -notlike "*$uvBinDir*")) {
        $pathsToAdd += $uvBinDir
        Write-Host "✅ Will add $uvBinDir to user PATH" -ForegroundColor $Green
    }
    
    # Add GOPATH bin directory to PATH for CloudFox
    $goPath = if ($env:GOPATH) { $env:GOPATH } else { "$env:USERPROFILE\go" }
    $goPathBin = "$goPath\bin"
    if ($currentPath -notlike "*$goPathBin*") {
        $pathsToAdd += $goPathBin
        Write-Host "✅ Will add $goPathBin to user PATH" -ForegroundColor $Green
        
        # Set GOPATH if not already set
        if (-not $env:GOPATH) {
            [System.Environment]::SetEnvironmentVariable("GOPATH", $goPath, "User")
            $env:GOPATH = $goPath
            Write-Host "✅ Set GOPATH to $goPath" -ForegroundColor $Green
        }
    }
    
    # Update PATH if there are paths to add
    if ($pathsToAdd.Count -gt 0) {
        $newPath = ($pathsToAdd -join ";") + ";" + $currentPath
        [System.Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
        
        # Update current session PATH
        foreach ($path in $pathsToAdd) {
            $env:PATH = "$path;$env:PATH"
        }
        
        Write-Host "✅ Updated user PATH with new directories" -ForegroundColor $Green
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
    Invoke-HitmonleeVerifyGo
    Invoke-HitmonleeVerifyCloudFox
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
