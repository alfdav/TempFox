#!/usr/bin/env python3

"""TempFox CLI orchestration."""

import argparse
import atexit
import getpass
import importlib.metadata
import json
import logging
import os
import subprocess
import sys

import tempfox.aws_profiles as aws_profiles
import tempfox.cloudfox as cloudfox
import tempfox.dependencies as dependencies

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def get_credential(env_var: str, prompt_text: str, secret: bool = False) -> str:
    """Check for existing credential and prompt user to use it or enter new one."""
    existing_value = os.environ.get(env_var)
    if existing_value:
        logging.info(f"Found existing {env_var} in environment variables.")
        use_existing = input(f"Would you like to use the existing {env_var}? (y/n): ")
        if use_existing.lower() == "y":
            return existing_value
    if secret:
        return getpass.getpass(prompt_text)
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


def validate_session_token(key_type: str, aws_session_token: str) -> bool:
    """Validate session token requirements by key type."""
    if key_type != "ASIA":
        return True
    return bool(aws_session_token.strip())


def test_aws_connection(
    aws_access_key_id: str, aws_secret_access_key: str, aws_session_token: str
) -> bool:
    """Test the AWS connection using the temporary credentials provided by the user."""
    try:
        aws_cmd = cloudfox.get_aws_cmd()

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
            if cloudfox.check_token_expiration(error_message):
                logging.warning(
                    "AWS token has expired. Please obtain new temporary credentials."
                )
                logging.info("Exiting script.")
                return False
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


def cleanup_on_exit() -> None:
    """Cleanup function to be called when script exits."""
    try:
        dependencies.cleanup_temp_files()
        cloudfox.cleanup_old_output_files()
    except Exception as e:
        logging.warning(f"Error during cleanup: {e}")


def get_version() -> str:
    """Get the package version."""
    try:
        return importlib.metadata.version("tempfox")
    except importlib.metadata.PackageNotFoundError:
        return "1.0.0"  # Fallback version


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

            profiles = aws_profiles.list_aws_profiles()
            tempfox_profiles = aws_profiles.get_tempfox_profiles()

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

            tempfox_profiles = aws_profiles.get_tempfox_profiles()

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
                    if aws_profiles.delete_aws_profile(profile):
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
        atexit.register(cleanup_on_exit)

        # Run pre-flight checks unless skipped
        if not args.skip_preflight:
            if not dependencies.run_preflight_checks():
                logging.error(
                    "❌ Pre-flight checks failed. Use --skip-preflight to bypass "
                    "(not recommended)"
                )
                sys.exit(1)
            logging.info("\n" + "=" * 50 + "\n")
        else:
            logging.warning("⚠️  Skipping pre-flight checks as requested")
            # Still check AWS CLI as it's critical
            if not dependencies.check_aws_cli():
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
            "AWS_SECRET_ACCESS_KEY",
            "Enter your AWS_SECRET_ACCESS_KEY: ",
            secret=True,
        )

        # Only prompt for session token if using ASIA (temporary credentials)
        if key_type == "ASIA":
            aws_session_token = get_credential(
                "AWS_SESSION_TOKEN",
                "Enter your AWS_SESSION_TOKEN: ",
                secret=True,
            )
            if not validate_session_token(key_type, aws_session_token):
                logging.error(
                    "AWS_SESSION_TOKEN is required when using ASIA temporary "
                    "credentials."
                )
                sys.exit(1)
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
                profile_config = aws_profiles.prompt_for_profile_creation(
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

                success = aws_profiles.create_aws_profile(
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

            cloudfox_success = cloudfox.run_cloudfox_aws_all_checks(
                aws_access_key_id, aws_secret_access_key, aws_session_token
            )

            if not cloudfox_success:
                logging.error("CloudFox analysis failed. Exiting.")
                sys.exit(1)

            # Final summary
            if profile_created and profile_config:
                logging.info("\n" + "=" * 60)
                logging.info("🎉 TempFox Session Complete")
                logging.info("=" * 60)
                profile_name = profile_config.get("profile_name", "tempfox-default")
                logging.info(f"✅ AWS profile '{profile_name}' is ready for reuse")
                logging.info("✅ CloudFox analysis completed")
                logging.info(
                    "\n💡 Your credentials are now saved for future AWS CLI usage!"
                )
        else:
            logging.error("AWS connection test failed. Exiting.")
            sys.exit(1)

    except KeyboardInterrupt:
        logging.warning("\n\n⚠️  Script interrupted by user. Exiting gracefully...")
        sys.exit(0)
    except Exception as e:
        logging.error(f"\n❌ Unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
