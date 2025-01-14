#!/usr/bin/env python3

r"""
  _____                   _____ 
 |_   _|__ _ __ ___  _ _|  ___|____  __
   | |/ _ \ '_ ` _ \| '_ \ |_ / _ \ \/ /
   | |  __/ | | | | | |_) |  _| (_) >  < 
   |_|\___|_| |_| |_| .__/|_|  \___/_/\_\
                     |_|                   

TempFox - AWS Credential Manager and CloudFox Integration Tool
Author: auslander
Version: 1.0
"""

import subprocess
import sys
import os
import json
import logging
import shutil
import glob
from datetime import datetime, timedelta
from pathlib import Path

# Constants
AWS_CLI_DOWNLOAD_URL = "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip"
AWS_CLI_ZIP = "awscliv2.zip"
MAX_OUTPUT_FILES = 5  # Maximum number of output files to keep
EXPIRED_TOKEN_INDICATORS = [
    "token has expired",
    "security token expired",
    "SecurityTokenExpired",
    "ExpiredToken"
]

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def cleanup_temp_files():
    """Clean up temporary files from AWS CLI installation."""
    try:
        if os.path.exists(AWS_CLI_ZIP):
            os.remove(AWS_CLI_ZIP)
        if os.path.exists("aws"):
            shutil.rmtree("aws")
    except Exception as e:
        logging.warning(f"Error cleaning up temporary files: {e}")

def install_aws_cli():
    """Install the AWS CLI on the user's Linux system."""
    try:
        # Download AWS CLI installer
        subprocess.run(
            ["curl", "-o", AWS_CLI_ZIP, AWS_CLI_DOWNLOAD_URL],
            check=True,
            timeout=300
        )
        
        # Unzip the installer
        subprocess.run(["unzip", "-o", AWS_CLI_ZIP], check=True)
        
        # Install AWS CLI
        subprocess.run(["sudo", "./aws/install"], check=True)
        
        logging.info("AWS CLI installed successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error installing AWS CLI: {e}")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        logging.error("Timeout while installing AWS CLI")
        sys.exit(1)
    finally:
        cleanup_temp_files()

def check_token_expiration(error_message):
    """Check if the error message indicates an expired token."""
    return any(indicator.lower() in error_message.lower() for indicator in EXPIRED_TOKEN_INDICATORS)

def get_aws_cmd():
    """Get the AWS CLI command path."""
    aws_cmd = shutil.which("aws")
    if not aws_cmd:
        raise FileNotFoundError("AWS CLI not found in PATH")
    return aws_cmd

def test_aws_connection(aws_access_key_id, aws_secret_access_key, aws_session_token):
    """Test the AWS connection using the temporary credentials provided by the user."""
    try:
        aws_cmd = get_aws_cmd()
        
        # Prepare environment variables
        env = os.environ.copy()
        env.update({
            "AWS_ACCESS_KEY_ID": aws_access_key_id,
            "AWS_SECRET_ACCESS_KEY": aws_secret_access_key,
            "AWS_SESSION_TOKEN": aws_session_token
        })
        
        # Capture the output and error messages
        process = subprocess.run(
            [aws_cmd, "sts", "get-caller-identity", "--output", "json"],
            env=env,
            capture_output=True,
            text=True,
            timeout=30
        )

        # Check for errors first
        if process.returncode != 0:
            error_message = process.stderr
            if check_token_expiration(error_message):
                logging.warning("AWS token has expired. Please obtain new temporary credentials.")
                proceed = input("Would you like to enter new credentials? (y/n): ")
                if proceed.lower() == 'y':
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

def get_aws_account_id(env):
    """Get the AWS account ID using the current credentials."""
    try:
        aws_cmd = get_aws_cmd()
        process = subprocess.run(
            [aws_cmd, "sts", "get-caller-identity", "--output", "json"],
            env=env,
            capture_output=True,
            text=True,
            timeout=30
        )
        if process.returncode == 0:
            identity = json.loads(process.stdout.strip())
            return identity.get('Account')
    except Exception as e:
        logging.error(f"Error getting AWS account ID: {e}")
    return None

def cleanup_old_output_files():
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

def run_cloudfox_aws_all_checks(aws_access_key_id, aws_secret_access_key, aws_session_token):
    """Run the 'cloudfox aws all-checks' command using the temporary credentials."""
    try:
        # Create a new environment with all current env variables plus AWS credentials
        env = os.environ.copy()
        env.update({
            "AWS_ACCESS_KEY_ID": aws_access_key_id,
            "AWS_SECRET_ACCESS_KEY": aws_secret_access_key,
            "AWS_SESSION_TOKEN": aws_session_token,
        })
        
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
            timeout=600  # 10 minute timeout
        )
        
        # Save text output
        with open(txt_output, 'w') as f:
            f.write(process.stdout)
        
        # Try to parse and save JSON output
        try:
            # Attempt to parse the output as JSON
            json_data = json.loads(process.stdout)
            with open(json_output, 'w') as f:
                json.dump(json_data, f, indent=2)
        except json.JSONDecodeError:
            # If output is not JSON, create a JSON object with the raw output
            with open(json_output, 'w') as f:
                json.dump({"raw_output": process.stdout}, f, indent=2)
        
        logging.info(f"CloudFox completed successfully. Results saved to {txt_output} and {json_output}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running 'cloudfox aws all-checks': {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

def get_credential(env_var, prompt_text):
    """Check for existing credential and prompt user to use it or enter new one."""
    existing_value = os.environ.get(env_var)
    if existing_value:
        logging.info(f"Found existing {env_var} in environment variables.")
        use_existing = input(f"Would you like to use the existing {env_var}? (y/n): ")
        if use_existing.lower() == 'y':
            return existing_value
    return input(prompt_text)

def check_access_key_type():
    """Prompt user for the type of AWS access key they're using."""
    while True:
        key_type = input("\nAre you using an AKIA (long-term) or ASIA (temporary) access key? (AKIA/ASIA): ").upper()
        if key_type in ['AKIA', 'ASIA']:
            return key_type
        logging.warning("Invalid input. Please enter either 'AKIA' or 'ASIA'.")

def check_aws_cli():
    """Check if AWS CLI is installed and get its version."""
    try:
        aws_cmd = get_aws_cmd()
        process = subprocess.run(
            [aws_cmd, "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if process.returncode == 0:
            logging.info(f"AWS CLI is already installed: {process.stdout.strip()}")
            return True
    except (subprocess.CalledProcessError, FileNotFoundError, Exception) as e:
        logging.info("AWS CLI is not installed. Installing now...")
        install_aws_cli()
        return True
    return False

def cleanup_on_exit():
    """Cleanup function to be called when script exits."""
    try:
        cleanup_temp_files()
        cleanup_old_output_files()
    except Exception as e:
        logging.warning(f"Error during cleanup: {e}")

def main():
    """Main function to run TempFox."""
    try:
        # Print welcome message
        logging.info("\n🦊 Welcome to TempFox - AWS Credential Manager and CloudFox Integration Tool")
        logging.info("=" * 70 + "\n")

        # Register cleanup function
        import atexit
        atexit.register(cleanup_on_exit)

        # Check if AWS CLI is installed
        if not check_aws_cli():
            logging.error("Failed to verify or install AWS CLI")
            sys.exit(1)

        # Check access key type
        key_type = check_access_key_type()

        # Get AWS credentials with individual checks
        aws_access_key_id = get_credential(
            "AWS_ACCESS_KEY_ID", 
            "Enter your AWS_ACCESS_KEY_ID: "
        )

        # Validate access key format
        if not aws_access_key_id.startswith(key_type):
            logging.warning(f"\n⚠️  Warning: The access key provided doesn't match the expected format ({key_type}...)")
            proceed = input("Do you want to proceed anyway? (y/n): ")
            if proceed.lower() != 'y':
                logging.info("Exiting script.")
                sys.exit(1)

        aws_secret_access_key = get_credential(
            "AWS_SECRET_ACCESS_KEY", 
            "Enter your AWS_SECRET_ACCESS_KEY: "
        )

        # Only prompt for session token if using ASIA (temporary credentials)
        if key_type == 'ASIA':
            aws_session_token = get_credential(
                "AWS_SESSION_TOKEN", 
                "Enter your AWS_SESSION_TOKEN: "
            )
        else:
            aws_session_token = ""
            logging.info("\nℹ️  Session token not required for AKIA (long-term) credentials.")

        # Test AWS connection
        if test_aws_connection(aws_access_key_id, aws_secret_access_key, aws_session_token):
            # Run 'cloudfox aws all-checks'
            run_cloudfox_aws_all_checks(aws_access_key_id, aws_secret_access_key, aws_session_token)

    except KeyboardInterrupt:
        logging.warning("\n\n⚠️  Script interrupted by user. Exiting gracefully...")
        sys.exit(0)
    except Exception as e:
        logging.error(f"\n❌ Unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
