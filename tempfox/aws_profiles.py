"""AWS profile and configuration management helpers."""

import configparser
import logging
import os
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Set


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
        "sa-east-1",  # Sao Paulo
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
