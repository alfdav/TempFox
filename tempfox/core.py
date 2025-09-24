#!/usr/bin/env python3

r"""
  _____                   _____
 |_   _|__ _ __ ___  _ _|  ___|____  __
   | |/ _ \ '_ ` _ \| '_ \ |_ / _ \ \/ /
   | |  __/ | | | | | |_) |  _| (_) >  <
   |_|\___|_| |_| |_| .__/|_|  \___/_/\_\
                     |_|

TempFox - AWS Credential Manager and CloudFox Integration Tool
Author: David Diazr
Version: 1.0
"""

import argparse
import configparser
import glob
import importlib.metadata
import json
import logging
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import urllib.request
import zipfile
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple

# Constants
MAX_OUTPUT_FILES = 5  # Maximum number of output files to keep
EXPIRED_TOKEN_INDICATORS = [
    "token has expired",
    "security token expired",
    "SecurityTokenExpired",
    "ExpiredToken",
]

# Go and CloudFox constants
GO_DOWNLOAD_BASE_URL = "https://go.dev/dl/"
CLOUDFOX_GITHUB_API = "https://api.github.com/repos/BishopFox/cloudfox/releases/latest"
CLOUDFOX_INSTALL_DIR = os.path.expanduser("~/.local/bin")
GO_INSTALL_DIR = os.path.expanduser("~/.local/go")

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


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


def get_aws_config_dir() -> str:
    """Get the AWS configuration directory path."""
    return os.path.expanduser("~/.aws")


def get_aws_credentials_file() -> str:
    """Get the AWS credentials file path."""
    return os.path.join(get_aws_config_dir(), "credentials")


def get_aws_config_file() -> str:
    """Get the AWS config file path."""
    return os.path.join(get_aws_config_dir(), "config")


def ensure_aws_config_dir() -> str:
    """Ensure the AWS configuration directory exists."""
    config_dir = get_aws_config_dir()
    os.makedirs(config_dir, exist_ok=True)
    return config_dir


def read_aws_credentials() -> configparser.ConfigParser:
    """Read the AWS credentials file and return a ConfigParser object."""
    credentials_file = get_aws_credentials_file()
    config = configparser.ConfigParser()

    if os.path.exists(credentials_file):
        try:
            config.read(credentials_file)
        except Exception as e:
            logging.warning(f"Error reading AWS credentials file: {e}")

    return config


def read_aws_config() -> configparser.ConfigParser:
    """Read the AWS config file and return a ConfigParser object."""
    config_file = get_aws_config_file()
    config = configparser.ConfigParser()

    if os.path.exists(config_file):
        try:
            config.read(config_file)
        except Exception as e:
            logging.warning(f"Error reading AWS config file: {e}")

    return config


def write_aws_credentials(config: configparser.ConfigParser) -> bool:
    """Write the AWS credentials configuration to file."""
    ensure_aws_config_dir()
    credentials_file = get_aws_credentials_file()

    try:
        with open(credentials_file, "w") as f:
            config.write(f)
        # Set proper file permissions (readable only by owner)
        os.chmod(credentials_file, 0o600)
        return True
    except Exception as e:
        logging.error(f"Error writing AWS credentials file: {e}")
        return False


def write_aws_config(config: configparser.ConfigParser) -> bool:
    """Write the AWS config configuration to file."""
    ensure_aws_config_dir()
    config_file = get_aws_config_file()

    try:
        with open(config_file, "w") as f:
            config.write(f)
        # Set proper file permissions (readable only by owner)
        os.chmod(config_file, 0o600)
        return True
    except Exception as e:
        logging.error(f"Error writing AWS config file: {e}")
        return False


def list_aws_profiles() -> List[str]:
    """List all available AWS profiles."""
    credentials_config = read_aws_credentials()
    config_config = read_aws_config()

    profiles: Set[str] = set()

    # Get profiles from credentials file
    for section in credentials_config.sections():
        profiles.add(section)

    # Get profiles from config file (they have "profile " prefix except for default)
    for section in config_config.sections():
        if section.startswith("profile "):
            profiles.add(section[8:])  # Remove "profile " prefix
        elif section == "default":
            profiles.add("default")

    return sorted(profiles)


def get_tempfox_profiles() -> List[str]:
    """Get all TempFox-created profiles."""
    all_profiles = list_aws_profiles()
    tempfox_profiles = [p for p in all_profiles if p.startswith("tempfox-")]
    return tempfox_profiles


def profile_exists(profile_name: str) -> bool:
    """Check if a profile already exists."""
    credentials_config = read_aws_credentials()
    config_config = read_aws_config()

    # Check in credentials file
    if credentials_config.has_section(profile_name):
        return True

    # Check in config file
    if profile_name == "default":
        if config_config.has_section("default"):
            return True
    else:
        if config_config.has_section(f"profile {profile_name}"):
            return True

    return False


def create_aws_profile(
    profile_name: str,
    aws_access_key_id: str,
    aws_secret_access_key: str,
    aws_session_token: Optional[str] = None,
    region: Optional[str] = None,
    output_format: str = "json",
) -> bool:
    """Create or update an AWS profile with the given credentials."""
    try:
        # Read existing configurations
        credentials_config = read_aws_credentials()
        config_config = read_aws_config()

        # Add/update credentials section
        if not credentials_config.has_section(profile_name):
            credentials_config.add_section(profile_name)

        credentials_config.set(profile_name, "aws_access_key_id", aws_access_key_id)
        credentials_config.set(
            profile_name, "aws_secret_access_key", aws_secret_access_key
        )

        if aws_session_token:
            credentials_config.set(profile_name, "aws_session_token", aws_session_token)
        elif credentials_config.has_option(profile_name, "aws_session_token"):
            # Remove session token if it exists but we don't have one
            credentials_config.remove_option(profile_name, "aws_session_token")

        # Add/update config section (for region and output format)
        config_section = (
            "default" if profile_name == "default" else f"profile {profile_name}"
        )

        if not config_config.has_section(config_section):
            config_config.add_section(config_section)

        if region:
            config_config.set(config_section, "region", region)
        if output_format:
            config_config.set(config_section, "output", output_format)

        # Write configurations to files
        if not write_aws_credentials(credentials_config):
            return False
        if not write_aws_config(config_config):
            return False

        return True

    except Exception as e:
        logging.error(f"Error creating AWS profile '{profile_name}': {e}")
        return False


def delete_aws_profile(profile_name: str) -> bool:
    """Delete an AWS profile."""
    try:
        credentials_config = read_aws_credentials()
        config_config = read_aws_config()

        # Remove from credentials file
        if credentials_config.has_section(profile_name):
            credentials_config.remove_section(profile_name)

        # Remove from config file
        config_section = (
            "default" if profile_name == "default" else f"profile {profile_name}"
        )
        if config_config.has_section(config_section):
            config_config.remove_section(config_section)

        # Write updated configurations
        write_aws_credentials(credentials_config)
        write_aws_config(config_config)

        return True

    except Exception as e:
        logging.error(f"Error deleting AWS profile '{profile_name}': {e}")
        return False


def generate_profile_name(aws_access_key_id: str, key_type: str) -> str:
    """Generate a unique profile name for TempFox."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Use last 8 characters of access key for uniqueness
    key_suffix = (
        aws_access_key_id[-8:] if len(aws_access_key_id) >= 8 else aws_access_key_id
    )
    profile_name = f"tempfox-{key_type.lower()}-{key_suffix}-{timestamp}"
    return profile_name


def get_aws_regions() -> List[str]:
    """Get a list of common AWS regions."""
    return [
        "us-east-1",  # N. Virginia
        "us-east-2",  # Ohio
        "us-west-1",  # N. California
        "us-west-2",  # Oregon
        "eu-west-1",  # Ireland
        "eu-west-2",  # London
        "eu-central-1",  # Frankfurt
        "ap-southeast-1",  # Singapore
        "ap-southeast-2",  # Sydney
        "ap-northeast-1",  # Tokyo
        "ca-central-1",  # Canada
        "sa-east-1",  # São Paulo
    ]


def prompt_for_profile_creation(
    aws_access_key_id: str,
    aws_secret_access_key: str,
    aws_session_token: str,
    key_type: str,
) -> Optional[Dict[str, Optional[str]]]:
    """Prompt user for profile creation options."""
    logging.info("\n" + "=" * 60)
    logging.info("🔐 AWS Profile Management")
    logging.info("=" * 60)

    # Show current profiles
    existing_profiles = list_aws_profiles()
    tempfox_profiles = get_tempfox_profiles()

    if existing_profiles:
        logging.info(f"\n📋 Existing AWS profiles ({len(existing_profiles)}):")
        for profile in existing_profiles:
            if profile in tempfox_profiles:
                logging.info(f"  • {profile} (TempFox)")
            else:
                logging.info(f"  • {profile}")
    else:
        logging.info("\n📋 No existing AWS profiles found.")

    # Ask if user wants to save credentials
    logging.info("\n💾 Would you like to save these credentials to an AWS profile?")
    logging.info("   This allows reuse with 'aws' command and other tools.")

    save_creds = input("\nSave credentials to AWS profile? (y/n): ").lower().strip()

    if save_creds != "y":
        logging.info("\n⚠️  Credentials will only be used for this TempFox session.")
        return None

    # Profile naming options
    logging.info("\n📛 Profile naming options:")
    logging.info("  1. Auto-generate unique name (recommended)")
    logging.info("  2. Custom profile name")
    logging.info("  3. Set as default profile")

    choice = input("\nChoose option (1-3): ").strip()

    if choice == "1":
        profile_name = generate_profile_name(aws_access_key_id, key_type)
    elif choice == "3":
        profile_name = "default"
        if profile_exists("default"):
            logging.warning("\n⚠️  A default profile already exists!")
            overwrite = (
                input("Overwrite existing default profile? (y/n): ").lower().strip()
            )
            if overwrite != "y":
                logging.info("Profile creation cancelled.")
                return None
    else:  # choice == "2" or invalid choice defaults to custom
        while True:
            profile_name = input("\nEnter custom profile name: ").strip()
            if not profile_name:
                logging.warning("Profile name cannot be empty.")
                continue
            if profile_exists(profile_name):
                logging.warning(f"\n⚠️  Profile '{profile_name}' already exists!")
                overwrite = input("Overwrite existing profile? (y/n): ").lower().strip()
                if overwrite == "y":
                    break
            else:
                break

    # Region selection
    logging.info("\n🌍 AWS Region selection:")
    regions = get_aws_regions()

    # Try to detect current region from AWS CLI config
    current_region = None
    try:
        result = subprocess.run(
            ["aws", "configure", "get", "region"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            current_region = result.stdout.strip()
    except Exception:
        pass

    if current_region and current_region in regions:
        logging.info(f"  0. Use current region: {current_region} (detected)")

    for i, region in enumerate(regions, 1):
        logging.info(f"  {i}. {region}")
    logging.info(f"  {len(regions) + 1}. Skip region configuration")

    region_choice = input(f"\nChoose region (0-{len(regions) + 1}): ").strip()

    try:
        choice_num = int(region_choice)
        if choice_num == 0 and current_region:
            selected_region = current_region
        elif 1 <= choice_num <= len(regions):
            selected_region = regions[choice_num - 1]
        else:
            selected_region = None
    except ValueError:
        selected_region = None

    return {
        "profile_name": profile_name,
        "region": selected_region,
        "output_format": "json",
    }


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


def check_token_expiration(error_message: str) -> bool:
    """Check if the error message indicates an expired token."""
    return any(
        indicator.lower() in error_message.lower()
        for indicator in EXPIRED_TOKEN_INDICATORS
    )


def get_aws_cmd() -> str:
    """Get the AWS CLI command path."""
    aws_cmd = shutil.which("aws")
    if not aws_cmd:
        raise FileNotFoundError("AWS CLI not found in PATH")
    return aws_cmd


def test_aws_connection(
    aws_access_key_id: str, aws_secret_access_key: str, aws_session_token: str
) -> bool:
    """Test the AWS connection using the temporary credentials provided by the user."""
    try:
        aws_cmd = get_aws_cmd()

        # Prepare environment variables
        env = os.environ.copy()
        env.update(
            {
                "AWS_ACCESS_KEY_ID": aws_access_key_id,
                "AWS_SECRET_ACCESS_KEY": aws_secret_access_key,
                "AWS_SESSION_TOKEN": aws_session_token,
            }
        )

        # Capture the output and error messages
        process = subprocess.run(
            [aws_cmd, "sts", "get-caller-identity", "--output", "json"],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Check for errors first
        if process.returncode != 0:
            error_message = process.stderr
            if check_token_expiration(error_message):
                logging.warning(
                    "AWS token has expired. Please obtain new temporary credentials."
                )
                proceed = input("Would you like to enter new credentials? (y/n): ")
                if proceed.lower() == "y":
                    main()
                else:
                    logging.info("Exiting script.")
                    sys.exit(1)
            else:
                logging.error(f"Error testing AWS connection: {error_message}")
                return False

        # Parse the JSON response to get identity information
        try:
            identity = json.loads(process.stdout.strip())
            logging.info("AWS connection successful! Running CloudFox")
            logging.info(f"Account: {identity.get('Account', 'N/A')}")
            logging.info(f"Arn: {identity.get('Arn', 'N/A')}")
            logging.info(f"UserId: {identity.get('UserId', 'N/A')}")
            return True
        except json.JSONDecodeError:
            logging.error("Error parsing AWS response")
            return False

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return False


def get_aws_account_id(env: Dict[str, str]) -> Optional[str]:
    """Get the AWS account ID using the current credentials."""
    try:
        aws_cmd = get_aws_cmd()
        process = subprocess.run(
            [aws_cmd, "sts", "get-caller-identity", "--output", "json"],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if process.returncode == 0:
            identity = json.loads(process.stdout.strip())
            account_id = identity.get("Account")
            return account_id if isinstance(account_id, str) else None
    except Exception as e:
        logging.error(f"Error getting AWS account ID: {e}")
    return None


def cleanup_old_output_files() -> None:
    """Clean up old output files, keeping only the most recent ones."""
    try:
        # Get all cloudfox output files
        txt_files = sorted(glob.glob("cloudfox_aws_*.txt"), reverse=True)
        json_files = sorted(glob.glob("cloudfox_aws_*.json"), reverse=True)

        # Remove old files keeping only MAX_OUTPUT_FILES most recent
        for old_file in txt_files[MAX_OUTPUT_FILES:]:
            os.remove(old_file)
        for old_file in json_files[MAX_OUTPUT_FILES:]:
            os.remove(old_file)
    except Exception as e:
        logging.warning(f"Error cleaning up old output files: {e}")


def run_cloudfox_aws_all_checks(
    aws_access_key_id: str, aws_secret_access_key: str, aws_session_token: str
) -> None:
    """Run the 'cloudfox aws all-checks' command using the temporary credentials."""
    try:
        # Create a new environment with all current env variables plus AWS credentials
        env = os.environ.copy()
        env.update(
            {
                "AWS_ACCESS_KEY_ID": aws_access_key_id,
                "AWS_SECRET_ACCESS_KEY": aws_secret_access_key,
                "AWS_SESSION_TOKEN": aws_session_token,
            }
        )

        # Get AWS account ID
        account_id = get_aws_account_id(env)
        if not account_id:
            logging.error("Could not retrieve AWS account ID")
            return

        # Clean up old output files
        cleanup_old_output_files()

        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create output filenames
        base_filename = f"cloudfox_aws_{account_id}_{timestamp}"
        txt_output = f"{base_filename}.txt"
        json_output = f"{base_filename}.json"

        # Run CloudFox and capture output
        process = subprocess.run(
            ["cloudfox", "aws", "all-checks"],
            env=env,
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout
        )

        # Save text output
        with open(txt_output, "w") as f:
            f.write(process.stdout)

        # Try to parse and save JSON output
        try:
            # Attempt to parse the output as JSON
            json_data = json.loads(process.stdout)
            with open(json_output, "w") as f:
                json.dump(json_data, f, indent=2)
        except json.JSONDecodeError:
            # If output is not JSON, create a JSON object with the raw output
            with open(json_output, "w") as f:
                json.dump({"raw_output": process.stdout}, f, indent=2)

        logging.info(
            f"CloudFox completed successfully. Results saved to {txt_output} "
            f"and {json_output}"
        )
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running 'cloudfox aws all-checks': {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")


def get_credential(env_var: str, prompt_text: str) -> str:
    """Check for existing credential and prompt user to use it or enter new one."""
    existing_value = os.environ.get(env_var)
    if existing_value:
        logging.info(f"Found existing {env_var} in environment variables.")
        use_existing = input(f"Would you like to use the existing {env_var}? (y/n): ")
        if use_existing.lower() == "y":
            return existing_value
    return input(prompt_text)


def check_access_key_type() -> str:
    """Prompt user for the type of AWS access key they're using."""
    while True:
        key_type = input(
            "\nAre you using an AKIA (long-term) or ASIA (temporary) access key? "
            "(AKIA/ASIA): "
        ).upper()
        if key_type in ["AKIA", "ASIA"]:
            return key_type
        logging.warning("Invalid input. Please enter either 'AKIA' or 'ASIA'.")


def check_aws_cli() -> bool:
    """Check if AWS CLI is installed and get its version."""
    try:
        aws_cmd = get_aws_cmd()
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


def cleanup_on_exit() -> None:
    """Cleanup function to be called when script exits."""
    try:
        cleanup_temp_files()
        cleanup_old_output_files()
    except Exception as e:
        logging.warning(f"Error during cleanup: {e}")


def get_version() -> str:
    """Get the package version."""
    try:
        return importlib.metadata.version("tempfox")
    except importlib.metadata.PackageNotFoundError:
        return "1.0.0"  # Fallback version


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

        download_url = f"https://go.dev/dl/{filename}"

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
            cloudfox_installed, version = check_cloudfox_installation()
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
    uv_installed, uv_version = check_uv_installation()
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
    go_installed, go_version = check_go_installation()
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
    cloudfox_installed, cloudfox_version = check_cloudfox_installation()
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


def main() -> None:
    """Main function to run TempFox."""
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(
            description="TempFox - AWS Credential Manager and CloudFox Integration Tool"
        )
        parser.add_argument(
            "--version", "-v", action="version", version=f"TempFox {get_version()}"
        )
        parser.add_argument(
            "--skip-preflight",
            action="store_true",
            help="Skip pre-flight dependency checks",
        )
        parser.add_argument(
            "--list-profiles",
            action="store_true",
            help="List all AWS profiles and exit",
        )
        parser.add_argument(
            "--cleanup-profiles",
            action="store_true",
            help="Clean up old TempFox profiles and exit",
        )
        parser.add_argument(
            "--no-profile", action="store_true", help="Skip profile creation prompts"
        )
        args = parser.parse_args()

        # Handle profile management commands
        if args.list_profiles:
            logging.info("\n🦊 TempFox - AWS Profile Manager")
            logging.info("=" * 40 + "\n")

            profiles = list_aws_profiles()
            tempfox_profiles = get_tempfox_profiles()

            if profiles:
                logging.info(f"📋 Found {len(profiles)} AWS profiles:")
                for profile in profiles:
                    if profile in tempfox_profiles:
                        logging.info(f"  • {profile} (TempFox)")
                    else:
                        logging.info(f"  • {profile}")

                if tempfox_profiles:
                    logging.info(f"\n🦊 TempFox profiles: {len(tempfox_profiles)}")
                    logging.info(
                        "💡 Use --cleanup-profiles to remove old TempFox profiles"
                    )
            else:
                logging.info("📋 No AWS profiles found.")

            sys.exit(0)

        if args.cleanup_profiles:
            logging.info("\n🦊 TempFox - Profile Cleanup")
            logging.info("=" * 40 + "\n")

            tempfox_profiles = get_tempfox_profiles()

            if not tempfox_profiles:
                logging.info("✅ No TempFox profiles found to clean up.")
                sys.exit(0)

            logging.info(f"🧹 Found {len(tempfox_profiles)} TempFox profiles:")
            for profile in tempfox_profiles:
                logging.info(f"  • {profile}")

            confirm = (
                input(f"\nDelete all {len(tempfox_profiles)} TempFox profiles? (y/n): ")
                .lower()
                .strip()
            )

            if confirm == "y":
                deleted_count = 0
                for profile in tempfox_profiles:
                    if delete_aws_profile(profile):
                        logging.info(f"✅ Deleted profile: {profile}")
                        deleted_count += 1
                    else:
                        logging.error(f"❌ Failed to delete profile: {profile}")

                logging.info(
                    f"\n🎉 Cleanup complete! Deleted {deleted_count}/"
                    f"{len(tempfox_profiles)} profiles."
                )
            else:
                logging.info("Cleanup cancelled.")

            sys.exit(0)

        # Print welcome message
        logging.info(
            "\n🦊 Welcome to TempFox - AWS Credential Manager and CloudFox "
            "Integration Tool"
        )
        logging.info("=" * 70 + "\n")

        # Register cleanup function
        import atexit

        atexit.register(cleanup_on_exit)

        # Run pre-flight checks unless skipped
        if not args.skip_preflight:
            if not run_preflight_checks():
                logging.error(
                    "❌ Pre-flight checks failed. Use --skip-preflight to bypass "
                    "(not recommended)"
                )
                sys.exit(1)
            logging.info("\n" + "=" * 50 + "\n")
        else:
            logging.warning("⚠️  Skipping pre-flight checks as requested")
            # Still check AWS CLI as it's critical
            if not check_aws_cli():
                logging.error("Failed to verify or install AWS CLI")
                sys.exit(1)

        # Check access key type
        key_type = check_access_key_type()

        # Get AWS credentials with individual checks
        aws_access_key_id = get_credential(
            "AWS_ACCESS_KEY_ID", "Enter your AWS_ACCESS_KEY_ID: "
        )

        # Validate access key format
        if not aws_access_key_id.startswith(key_type):
            logging.warning(
                f"\n⚠️  Warning: The access key provided doesn't match the "
                f"expected format ({key_type}...)"
            )
            proceed = input("Do you want to proceed anyway? (y/n): ")
            if proceed.lower() != "y":
                logging.info("Exiting script.")
                sys.exit(1)

        aws_secret_access_key = get_credential(
            "AWS_SECRET_ACCESS_KEY", "Enter your AWS_SECRET_ACCESS_KEY: "
        )

        # Only prompt for session token if using ASIA (temporary credentials)
        if key_type == "ASIA":
            aws_session_token = get_credential(
                "AWS_SESSION_TOKEN", "Enter your AWS_SESSION_TOKEN: "
            )
        else:
            aws_session_token = ""
            logging.info(
                "\nℹ️  Session token not required for AKIA (long-term) credentials."
            )

        # Test AWS connection
        if test_aws_connection(
            aws_access_key_id, aws_secret_access_key, aws_session_token
        ):
            # Offer profile creation after successful connection (unless disabled)
            profile_config = None
            if not args.no_profile:
                profile_config = prompt_for_profile_creation(
                    aws_access_key_id,
                    aws_secret_access_key,
                    aws_session_token,
                    key_type,
                )
            else:
                logging.info("\n⚠️  Profile creation skipped (--no-profile flag)")

            profile_created = False
            if profile_config:
                logging.info(
                    f"\n📝 Creating AWS profile: {profile_config['profile_name']}"
                )

                success = create_aws_profile(
                    profile_config["profile_name"] or "tempfox-default",
                    aws_access_key_id,
                    aws_secret_access_key,
                    aws_session_token,
                    profile_config["region"],
                    profile_config["output_format"] or "json",
                )

                if success:
                    logging.info(
                        f"✅ AWS profile '{profile_config['profile_name']}' "
                        f"created successfully!"
                    )

                    # Show usage instructions
                    logging.info("\n📖 Profile usage instructions:")
                    if profile_config["profile_name"] == "default":
                        logging.info("  • aws sts get-caller-identity")
                        logging.info("  • aws s3 ls")
                        logging.info("  • cloudfox aws all-checks")
                    else:
                        logging.info(
                            f"  • aws --profile {profile_config['profile_name']} "
                            f"sts get-caller-identity"
                        )
                        logging.info(
                            f"  • aws --profile {profile_config['profile_name']} s3 ls"
                        )
                        logging.info(
                            f"  • cloudfox aws --profile "
                            f"{profile_config['profile_name']} all-checks"
                        )

                    profile_created = True
                else:
                    logging.error(
                        f"❌ Failed to create profile "
                        f"'{profile_config['profile_name']}'"
                    )

            # Run CloudFox
            logging.info("\n" + "=" * 60)
            logging.info("🦊 Running CloudFox Security Analysis")
            logging.info("=" * 60)

            run_cloudfox_aws_all_checks(
                aws_access_key_id, aws_secret_access_key, aws_session_token
            )

            # Final summary
            if profile_created and profile_config:
                logging.info("\n" + "=" * 60)
                logging.info("🎉 TempFox Session Complete")
                logging.info("=" * 60)
                profile_name = profile_config.get("profile_name", "tempfox-default")
                logging.info(
                    f"✅ AWS profile '{profile_name}' is ready for reuse"
                )
                logging.info("✅ CloudFox analysis completed")
                logging.info(
                    "\n💡 Your credentials are now saved for future AWS CLI usage!"
                )

    except KeyboardInterrupt:
        logging.warning("\n\n⚠️  Script interrupted by user. Exiting gracefully...")
        sys.exit(0)
    except Exception as e:
        logging.error(f"\n❌ Unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
