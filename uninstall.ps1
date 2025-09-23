# TempFox Uninstallation Script for Windows with UV Support
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
# Hitmonlee: System verification - uses powerful kicks to check installation status
function Invoke-HitmonleeVerifyInstallation {
    Write-Host "🥋 Hitmonlee is checking TempFox installation with High Jump Kick..." -ForegroundColor $Blue
    
    if (-not (Test-Path $InstallDir) -and -not (Test-Path "$BinDir\tempfox.bat")) {
        Write-Host "⚠️  TempFox doesn't appear to be installed." -ForegroundColor $Yellow
        exit 0
    }
    
    Write-Host "✅ TempFox installation found" -ForegroundColor $Green
}

# Primeape: Cleanup operations - uses rage to forcefully remove files
function Invoke-PrimeapeRemoveInstallation {
    Write-Host "😡 Primeape is removing TempFox installation with Rage..." -ForegroundColor $Blue
    
    # Remove installation directory
    if (Test-Path $InstallDir) {
        Write-Host "🗑️  Removing installation directory: $InstallDir" -ForegroundColor $Yellow
        Remove-Item $InstallDir -Recurse -Force
    }
    
    Write-Host "✅ TempFox files removed" -ForegroundColor $Green
}

# Machamp: Environment cleanup - uses four arms to clean multiple configurations
function Invoke-MachampCleanupEnvironment {
    Write-Host "🔧 Machamp is cleaning environment variables with Dynamic Punch..." -ForegroundColor $Blue
    
    # Get current user PATH
    $currentPath = [System.Environment]::GetEnvironmentVariable("PATH", "User")
    
    # Remove TempFox bin directory from PATH
    if ($currentPath -like "*$BinDir*") {
        $newPath = $currentPath -replace [regex]::Escape("$BinDir;"), ""
        $newPath = $newPath -replace [regex]::Escape(";$BinDir"), ""
        $newPath = $newPath -replace [regex]::Escape("$BinDir"), ""
        
        [System.Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
        Write-Host "✅ Removed $BinDir from user PATH" -ForegroundColor $Green
    } else {
        Write-Host "ℹ️  PATH was not modified by TempFox" -ForegroundColor $Yellow
    }
}

# Machoke: Directory cleanup - uses powerful muscles to clean empty directories
function Invoke-MachokeCleanupDirectories {
    Write-Host "💪 Machoke is cleaning empty directories with Strength..." -ForegroundColor $Blue
    
    # Remove empty parent directories if they exist and are empty
    $parentDir = Split-Path $InstallDir -Parent
    if ((Test-Path $parentDir) -and ((Get-ChildItem $parentDir | Measure-Object).Count -eq 0)) {
        Remove-Item $parentDir -Force
        Write-Host "✅ Removed empty parent directory" -ForegroundColor $Green
    }
}

# Hitmonchan: User feedback - uses punching combinations to deliver messages
function Invoke-HitmonchanShowSuccess {
    Write-Host "👊 Hitmonchan delivers the final message with Thunder Punch..." -ForegroundColor $Blue
    Write-Host ""
    Write-Host "🎉 TempFox uninstallation completed successfully!" -ForegroundColor $Green
    Write-Host ""
    Write-Host "📋 Final steps:" -ForegroundColor $Yellow
    Write-Host "   1. Restart your PowerShell session or terminal"
    Write-Host "   2. Verify removal: " -NoNewline; Write-Host "Get-Command tempfox" -ForegroundColor $Blue -NoNewline; Write-Host " (should return an error)"
    Write-Host ""
    Write-Host "🔗 Thank you for using TempFox!" -ForegroundColor $Blue
    Write-Host ""
}

# Main uninstallation process
function Main {
    Write-Host "🦊 TempFox Uninstallation Script for Windows" -ForegroundColor $Green
    Write-Host "Using Fighting-type Pokemon for system operations!" -ForegroundColor $Blue
    Write-Host ""
    
    # Confirm uninstallation
    if (-not $Force) {
        Write-Host "⚠️  This will completely remove TempFox from your system." -ForegroundColor $Yellow
        $confirmation = Read-Host "Are you sure you want to continue? (y/N)"
        
        if ($confirmation -notmatch "^[Yy]$") {
            Write-Host "ℹ️  Uninstallation cancelled." -ForegroundColor $Blue
            exit 0
        }
    }
    
    Invoke-HitmonleeVerifyInstallation
    Invoke-PrimeapeRemoveInstallation
    Invoke-MachampCleanupEnvironment
    Invoke-MachokeCleanupDirectories
    Invoke-HitmonchanShowSuccess
}

# Run main function
try {
    Main
}
catch {
    Write-Host "❌ Uninstallation failed: $($_.Exception.Message)" -ForegroundColor $Red
    exit 1
}
