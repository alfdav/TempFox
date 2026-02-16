"""Dependency installation and pre-flight checks."""

import logging
import os
import platform
import shutil
import subprocess
import tarfile
import urllib.request
import zipfile
from typing import Optional, Tuple

GO_DOWNLOAD_BASE_URL = "https://go.dev/dl/"
GO_INSTALL_DIR = os.path.expanduser("~/.local/go")


def cleanup_temp_files() -> None:
    """Clean up temporary files from installations."""
    try:
        # AWS CLI temp files
        temp_files = [
            "awscliv2.zip",
            "AWSCLIV2.pkg",
            "AWSCLIV2.msi",
            "AWSCLIV2-arm64.pkg",
            "AWSCLIV2-arm64.msi",
        ]
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)

        # AWS installer directory
        if os.path.exists("aws"):
            shutil.rmtree("aws")

    except Exception as e:
        logging.warning(f"Error cleaning up temporary files: {e}")


def get_platform_info() -> Tuple[str, str]:
    """Get platform information for binary downloads."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    # Normalize architecture names
    if machine in ["x86_64", "amd64"]:
        arch = "amd64"
    elif machine in ["aarch64", "arm64"]:
        arch = "arm64"
    elif machine.startswith("arm"):
        arch = "arm"
    else:
        arch = machine

    return system, arch


def get_aws_cli_download_url() -> str:
    """Get the appropriate AWS CLI download URL for the current platform."""
    system, arch = get_platform_info()

    if system == "darwin":  # macOS
        if arch == "arm64":
            return "https://awscli.amazonaws.com/AWSCLIV2-arm64.pkg"
        else:
            return "https://awscli.amazonaws.com/AWSCLIV2.pkg"
    elif system == "linux":
        if arch == "arm64":
            return "https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip"
        else:
            return "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip"
    elif system == "windows":
        if arch == "arm64":
            return "https://awscli.amazonaws.com/AWSCLIV2-arm64.msi"
        else:
            return "https://awscli.amazonaws.com/AWSCLIV2.msi"
    else:
        raise ValueError(f"Unsupported platform: {system}-{arch}")


def install_aws_cli() -> bool:
    """Install the AWS CLI for the current platform."""
    try:
        system, arch = get_platform_info()
        download_url = get_aws_cli_download_url()

        logging.info(f"📦 Installing AWS CLI for {system}-{arch}...")

        if system == "darwin":  # macOS
            # Download the pkg file
            pkg_file = "AWSCLIV2.pkg"
            subprocess.run(
                ["curl", "-o", pkg_file, download_url], check=True, timeout=300
            )

            # Install using installer
            subprocess.run(
                ["sudo", "installer", "-pkg", pkg_file, "-target", "/"], check=True
            )

            # Cleanup
            os.remove(pkg_file)

        elif system == "linux":
            # Download ZIP file
            zip_file = "awscliv2.zip"
            subprocess.run(
                ["curl", "-o", zip_file, download_url], check=True, timeout=300
            )

            # Unzip the installer
            subprocess.run(["unzip", "-o", zip_file], check=True)

            # Install AWS CLI
            subprocess.run(["sudo", "./aws/install"], check=True)

            # Cleanup
            os.remove(zip_file)
            if os.path.exists("aws"):
                shutil.rmtree("aws")

        elif system == "windows":
            # Download MSI file
            msi_file = "AWSCLIV2.msi"
            subprocess.run(
                ["curl", "-o", msi_file, download_url], check=True, timeout=300
            )

            # Install using msiexec
            subprocess.run(["msiexec", "/i", msi_file, "/quiet"], check=True)

            # Cleanup
            os.remove(msi_file)

        logging.info("✅ AWS CLI installed successfully")
        return True

    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Error installing AWS CLI: {e}")
        return False
    except subprocess.TimeoutExpired:
        logging.error("❌ Timeout while installing AWS CLI")
        return False
    except Exception as e:
        logging.error(f"❌ Unexpected error installing AWS CLI: {e}")
        return False
    finally:
        cleanup_temp_files()


def check_aws_cli() -> bool:
    """Check if AWS CLI is installed and get its version."""
    try:
        aws_cmd = shutil.which("aws")
        if not aws_cmd:
            raise FileNotFoundError("AWS CLI not found")

        process = subprocess.run(
            [aws_cmd, "--version"], capture_output=True, text=True, timeout=10
        )
        if process.returncode == 0:
            logging.info(f"AWS CLI is already installed: {process.stdout.strip()}")
            return True
    except (subprocess.CalledProcessError, FileNotFoundError, Exception):
        logging.info("AWS CLI is not installed. Installing now...")
        return install_aws_cli()
    return False


def check_go_installation() -> Tuple[bool, Optional[str]]:
    """Check if Go is installed and return version info."""
    try:
        go_cmd = shutil.which("go")
        if not go_cmd:
            return False, None

        process = subprocess.run(
            ["go", "version"], capture_output=True, text=True, timeout=10
        )

        if process.returncode == 0:
            version_output = process.stdout.strip()
            logging.info(f"Go is installed: {version_output}")
            return True, version_output
        else:
            return False, None

    except (subprocess.CalledProcessError, FileNotFoundError, Exception) as e:
        logging.debug(f"Go check failed: {e}")
        return False, None


def install_go() -> bool:
    """Install Go binary for the current platform."""
    try:
        system, arch = get_platform_info()

        # Get latest Go version from the download page
        logging.info("🔍 Fetching latest Go version...")

        # For simplicity, we'll use a known stable version
        # In production, you might want to scrape the Go download page
        go_version = "1.21.5"  # Update this as needed

        if system == "darwin":
            filename = f"go{go_version}.darwin-{arch}.tar.gz"
        elif system == "linux":
            filename = f"go{go_version}.linux-{arch}.tar.gz"
        elif system == "windows":
            filename = f"go{go_version}.windows-{arch}.zip"
        else:
            logging.error(f"Unsupported platform: {system}-{arch}")
            return False

        download_url = f"{GO_DOWNLOAD_BASE_URL}{filename}"

        logging.info(f"📦 Downloading Go from {download_url}")

        # Create installation directory
        os.makedirs(GO_INSTALL_DIR, exist_ok=True)

        # Download Go
        temp_file = f"/tmp/{filename}"
        urllib.request.urlretrieve(download_url, temp_file)

        # Extract Go
        logging.info("📂 Extracting Go...")
        if filename.endswith(".tar.gz"):
            with tarfile.open(temp_file, "r:gz") as tar:
                tar.extractall(GO_INSTALL_DIR)
        elif filename.endswith(".zip"):
            with zipfile.ZipFile(temp_file, "r") as zip_ref:
                zip_ref.extractall(GO_INSTALL_DIR)

        # Clean up
        os.remove(temp_file)

        # Add Go to PATH for current session
        go_bin_path = os.path.join(GO_INSTALL_DIR, "go", "bin")
        current_path = os.environ.get("PATH", "")
        if go_bin_path not in current_path:
            os.environ["PATH"] = f"{go_bin_path}:{current_path}"

        logging.info("✅ Go installed successfully")
        return True

    except Exception as e:
        logging.error(f"❌ Error installing Go: {e}")
        return False


def check_cloudfox_installation() -> Tuple[bool, Optional[str]]:
    """Check if CloudFox is installed and return version info."""
    try:
        cloudfox_cmd = shutil.which("cloudfox")
        if not cloudfox_cmd:
            return False, None

        process = subprocess.run(
            ["cloudfox", "--version"], capture_output=True, text=True, timeout=10
        )

        if process.returncode == 0:
            version_output = process.stdout.strip()
            logging.info(f"CloudFox is installed: {version_output}")
            return True, version_output
        else:
            # Try alternative version check
            process = subprocess.run(
                ["cloudfox", "--help"], capture_output=True, text=True, timeout=10
            )
            if process.returncode == 0:
                logging.info("CloudFox is installed (version check unavailable)")
                return True, "CloudFox (version unknown)"
            return False, None

    except (subprocess.CalledProcessError, FileNotFoundError, Exception) as e:
        logging.debug(f"CloudFox check failed: {e}")
        return False, None


def install_cloudfox() -> bool:
    """Install CloudFox binary for the current platform."""
    try:
        # First, ensure Go is available
        go_installed, _ = check_go_installation()
        if not go_installed:
            logging.info(
                "🔧 Go is required for CloudFox installation. Installing Go first..."
            )
            if not install_go():
                logging.error(
                    "❌ Failed to install Go. Cannot proceed with CloudFox "
                    "installation."
                )
                return False

        logging.info("📦 Installing CloudFox using Go...")

        # Install CloudFox using go install
        process = subprocess.run(
            ["go", "install", "github.com/BishopFox/cloudfox@latest"],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout for compilation
        )

        if process.returncode == 0:
            logging.info("✅ CloudFox installed successfully via Go")

            # Check if CloudFox is in PATH
            cloudfox_installed, _ = check_cloudfox_installation()
            if not cloudfox_installed:
                # Add GOPATH/bin to PATH if needed
                gopath = os.environ.get("GOPATH", os.path.expanduser("~/go"))
                gobin = os.path.join(gopath, "bin")
                current_path = os.environ.get("PATH", "")
                if gobin not in current_path:
                    os.environ["PATH"] = f"{gobin}:{current_path}"
                    logging.info(f"Added {gobin} to PATH")

            return True
        else:
            logging.error(f"❌ Failed to install CloudFox: {process.stderr}")
            return False

    except Exception as e:
        logging.error(f"❌ Error installing CloudFox: {e}")
        return False


def check_uv_installation() -> Tuple[bool, Optional[str]]:
    """Check if UV package manager is installed."""
    try:
        uv_cmd = shutil.which("uv")
        if not uv_cmd:
            return False, None

        process = subprocess.run(
            ["uv", "--version"], capture_output=True, text=True, timeout=10
        )

        if process.returncode == 0:
            version_output = process.stdout.strip()
            logging.info(f"UV is installed: {version_output}")
            return True, version_output
        else:
            return False, None

    except (subprocess.CalledProcessError, FileNotFoundError, Exception) as e:
        logging.debug(f"UV check failed: {e}")
        return False, None


def run_preflight_checks() -> bool:
    """Run comprehensive pre-flight checks for all dependencies."""
    logging.info("🚀 Running TempFox pre-flight checks...")
    logging.info("=" * 50)

    checks_passed = True

    # Check AWS CLI
    logging.info("1️⃣ Checking AWS CLI...")
    if not check_aws_cli():
        logging.error("❌ AWS CLI check failed")
        checks_passed = False
    else:
        logging.info("✅ AWS CLI is ready")

    # Check UV installation (optional but recommended)
    logging.info("\n2️⃣ Checking UV package manager...")
    uv_installed, _ = check_uv_installation()
    if not uv_installed:
        logging.warning(
            "⚠️  UV is not installed. This is optional but recommended for "
            "faster package management."
        )
        logging.info(
            "💡 You can install UV later from: https://github.com/astral-sh/uv"
        )
        logging.info("💡 TempFox will work with regular pip as well.")
    else:
        logging.info("✅ UV is ready")

    # Check Go installation
    logging.info("\n3️⃣ Checking Go installation...")
    go_installed, _ = check_go_installation()
    if not go_installed:
        logging.warning("⚠️  Go is not installed. Installing now...")
        if install_go():
            logging.info("✅ Go installation completed")
        else:
            logging.error("❌ Go installation failed")
            checks_passed = False
    else:
        logging.info("✅ Go is ready")

    # Check CloudFox installation
    logging.info("\n4️⃣ Checking CloudFox installation...")
    cloudfox_installed, _ = check_cloudfox_installation()
    if not cloudfox_installed:
        logging.warning("⚠️  CloudFox is not installed. Installing now...")
        if install_cloudfox():
            logging.info("✅ CloudFox installation completed")
        else:
            logging.error("❌ CloudFox installation failed")
            checks_passed = False
    else:
        logging.info("✅ CloudFox is ready")

    # Final verification
    logging.info("\n🔍 Final verification...")
    if checks_passed:
        # Re-verify all tools are working
        try:
            subprocess.run(
                ["aws", "--version"], capture_output=True, check=True, timeout=10
            )
            subprocess.run(
                ["go", "version"], capture_output=True, check=True, timeout=10
            )
            subprocess.run(
                ["cloudfox", "--help"], capture_output=True, check=True, timeout=10
            )

            logging.info("✅ All pre-flight checks passed!")
            logging.info("🦊 TempFox is ready to run!")
            return True
        except Exception as e:
            logging.error(f"❌ Final verification failed: {e}")
            return False
    else:
        logging.error(
            "❌ Some pre-flight checks failed. Please resolve the issues above."
        )
        return False
