"""CloudFox execution and AWS identity helper functions."""

import glob
import json
import logging
import os
import shutil
import subprocess
from datetime import datetime
from typing import Dict, Optional

MAX_OUTPUT_FILES = 5  # Maximum number of output files to keep
EXPIRED_TOKEN_INDICATORS = [
    "token has expired",
    "security token expired",
    "SecurityTokenExpired",
    "ExpiredToken",
]


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
