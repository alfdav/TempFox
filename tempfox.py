#!/usr/bin/env python3

r"""
  _____                   _____ 
 |_   _|__ _ __ ___  _ _|  ___|____  __
   | |/ _ \ '_ ` _ \| '_ \ |_ / _ \ \/ /
   | |  __/ | | | | | |_) |  _| (_) >  < 
   |_|\___|_| |_| |_| .__/|_|  \___/_/\_\
                     |_|                   

TempFox - AWS Credential Manager and CloudFox Integration Tool
Author: alfdav
Version: 0.11
"""

import subprocess
import sys
import os
import json

def install_aws_cli():
    """
    Install the AWS CLI on the user's Linux system.
    """
    try:
        subprocess.run("curl https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip -o awscliv2.zip", shell=True, check=True)
        subprocess.run("unzip awscliv2.zip", shell=True, check=True)
        subprocess.run("sudo ./aws/install", shell=True, cwd=os.getcwd(), check=True)
        print("AWS CLI installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing AWS CLI: {e}")
        sys.exit(1)

def check_token_expiration(error_message):
    """
    Check if the error message indicates an expired token.
    """
    expired_indicators = [
        "token has expired",
        "security token expired",
        "SecurityTokenExpired",
        "ExpiredToken"
    ]
    return any(indicator.lower() in error_message.lower() for indicator in expired_indicators)

def test_aws_connection(aws_access_key_id, aws_secret_access_key, aws_session_token):
    """
    Test the AWS connection using the temporary credentials provided by the user.
    """
    try:
        # Capture the output and error messages
        process = subprocess.run(
            "/usr/local/bin/aws sts get-caller-identity --output json",
            shell=True,
            env={
                "AWS_ACCESS_KEY_ID": aws_access_key_id,
                "AWS_SECRET_ACCESS_KEY": aws_secret_access_key,
                "AWS_SESSION_TOKEN": aws_session_token,
                "PATH": os.environ.get("PATH", "")
            },
            capture_output=True,
            text=True
        )

        # Check for errors first
        if process.returncode != 0:
            error_message = process.stderr
            if check_token_expiration(error_message):
                print("\n⚠️  Error: AWS token has expired. Please obtain new temporary credentials.")
                proceed = input("Would you like to enter new credentials? (y/n): ")
                if proceed.lower() == 'y':
                    main()
                else:
                    print("Exiting script.")
                    sys.exit(1)
            else:
                print(f"Error testing AWS connection: {error_message}")
                return False

        # Parse the JSON response to get identity information
        try:
            identity = json.loads(process.stdout.strip())
            print("\n✅ AWS connection successful!")
            print(f"Account: {identity.get('Account', 'N/A')}")
            print(f"Arn: {identity.get('Arn', 'N/A')}")
            print(f"UserId: {identity.get('UserId', 'N/A')}\n")
            return True
        except json.JSONDecodeError:
            print("Error parsing AWS response")
            return False

    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def run_cloudfox_aws_all_checks(aws_access_key_id, aws_secret_access_key, aws_session_token):
    """
    Run the 'cloudfox aws all-checks' command using the temporary credentials.
    """
    try:
        # Create a new environment with all current env variables plus AWS credentials
        env = os.environ.copy()
        env.update({
            "AWS_ACCESS_KEY_ID": aws_access_key_id,
            "AWS_SECRET_ACCESS_KEY": aws_secret_access_key,
            "AWS_SESSION_TOKEN": aws_session_token,
        })
        
        subprocess.run("cloudfox aws all-checks", shell=True, env=env)
        print("'cloudfox aws all-checks' completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running 'cloudfox aws all-checks': {e}")

def get_credential(env_var, prompt_text):
    """
    Check for existing credential and prompt user to use it or enter new one.
    """
    existing_value = os.environ.get(env_var)
    if existing_value:
        print(f"Found existing {env_var} in environment variables.")
        use_existing = input(f"Would you like to use the existing {env_var}? (y/n): ")
        if use_existing.lower() == 'y':
            return existing_value
    return input(prompt_text)

def check_access_key_type():
    """
    Prompt user for the type of AWS access key they're using.
    """
    while True:
        key_type = input("\nAre you using an AKIA (long-term) or ASIA (temporary) access key? (AKIA/ASIA): ").upper()
        if key_type in ['AKIA', 'ASIA']:
            return key_type
        print("Invalid input. Please enter either 'AKIA' or 'ASIA'.")

def main():
    try:
        # Print welcome message
        print("\n🦊 Welcome to TempFox - AWS Credential Manager and CloudFox Integration Tool")
        print("=" * 70 + "\n")

        # Check if AWS CLI is installed
        try:
            subprocess.run("/usr/local/bin/aws --version", shell=True, check=True)
            print("✅ AWS CLI is already installed.")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚙️  AWS CLI is not installed. Installing now...")
            install_aws_cli()

        # Check access key type
        key_type = check_access_key_type()

        # Get AWS credentials with individual checks
        aws_access_key_id = get_credential(
            "AWS_ACCESS_KEY_ID", 
            "Enter your AWS_ACCESS_KEY_ID: "
        )

        # Validate access key format
        if not aws_access_key_id.startswith(key_type):
            print(f"\n⚠️  Warning: The access key provided doesn't match the expected format ({key_type}...)")
            proceed = input("Do you want to proceed anyway? (y/n): ")
            if proceed.lower() != 'y':
                print("Exiting script.")
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
            print("\nℹ️  Session token not required for AKIA (long-term) credentials.")

        # Test AWS connection
        if test_aws_connection(aws_access_key_id, aws_secret_access_key, aws_session_token):
            # Run 'cloudfox aws all-checks'
            run_cloudfox_aws_all_checks(aws_access_key_id, aws_secret_access_key, aws_session_token)

    except KeyboardInterrupt:
        print("\n\n⚠️  Script interrupted by user. Exiting gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
