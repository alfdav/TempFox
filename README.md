# 🦊 TempFox

## Description
TempFox is a streamlined Python tool that manages AWS credentials and automates CloudFox security checks. It elegantly handles both long-term (AKIA) and temporary (ASIA) AWS credentials, offering robust token validation and credential management.

```
  _____                   _____ 
 |_   _|__ _ __ ___  _ _|  ___|____  __
   | |/ _ \ '_ ` _ \| '_ \ |_ / _ \ \/ /
   | |  __/ | | | | | |_) |  _| (_) >  < 
   |_|\___|_| |_| |_| .__/|_|  \___/_/\_\
                     |_|                   
```

## Key Features
- 🔄 Automatic AWS CLI installation
- 🔑 Support for both AKIA (long-term) & ASIA (temporary) credentials
- ⏰ Token expiration handling
- ✅ Smart credential format validation
- 🔍 Environment variable detection
- 🧪 AWS connection testing with detailed identity information
- 🦊 Integrated CloudFox AWS security checks
- 💻 Interactive user experience

## Quick Start
```bash
# Clone the repository
git clone https://github.com/yourusername/tempfox.git

# Navigate to TempFox directory
cd tempfox

# Make script executable
chmod +x tempfox.py

# Run TempFox
python3 tempfox.py
```

## Prerequisites
- Python 3.x
- Linux operating system
- Internet connection
- CloudFox installed
- Sudo privileges (for AWS CLI installation if needed)

## How It Works

### 1. Credential Management
- Detects and offers to reuse existing AWS credentials
- Validates AKIA/ASIA credential format
- Handles token expiration gracefully
- Processes AWS temporary security tokens

### 2. AWS CLI Integration
- Automatic installation if not present
- Tests AWS connectivity
- Displays detailed identity information:
  - Account ID
  - ARN
  - User ID

### 3. CloudFox Integration
- Seamlessly executes CloudFox AWS all security checks
- Maintains environment variables
- (Somewhat) Handles execution errors

## Usage Examples

### First Time Setup
```bash
$ python3 tempfox.py
🦊 Welcome to TempFox - AWS Credential Manager and CloudFox Integration Tool
======================================================================

⚙️  AWS CLI is not installed. Installing now...
✅ AWS CLI installed successfully.

Are you using an AKIA (long-term) or ASIA (temporary) access key? (AKIA/ASIA): ASIA
Enter your AWS_ACCESS_KEY_ID: ASIA...
Enter your AWS_SECRET_ACCESS_KEY: ****
Enter your AWS_SESSION_TOKEN: ****

✅ AWS connection successful!
Account: 123456789012
Arn: arn:aws:sts::123456789012:assumed-role/example-role/session-name
UserId: AROA...
```

### With Existing Credentials
```bash
$ python3 tempfox.py
🦊 Welcome to TempFox - AWS Credential Manager and CloudFox Integration Tool
======================================================================

✅ AWS CLI is already installed.

Are you using an AKIA (long-term) or ASIA (temporary) access key? (AKIA/ASIA): ASIA
Found existing AWS_ACCESS_KEY_ID in environment variables.
Would you like to use the existing AWS_ACCESS_KEY_ID? (y/n): y
```

## Troubleshooting

### Common Issues and Solutions

1. **AWS CLI Installation**
   ```bash
   Error installing AWS CLI: [Errno 13] Permission denied
   ```
   - Run with sudo privileges
   - Check internet connection
   - Verify system architecture

2. **Credential Format**
   ```bash
   ⚠️  Warning: The access key provided doesn't match the expected format (ASIA...)
   ```
   - Verify credential type (AKIA/ASIA)
   - Check for typing errors
   - Confirm credential format

3. **Token Expiration**
   ```bash
   ⚠️  Error: AWS token has expired. Please obtain new temporary credentials.
   ```
   - Obtain new temporary credentials
   - Check token validity period
   - Verify token permissions

## Contributing
Contributions are welcome! Feel free to:
- Submit issues
- Fork the repository
- Create pull requests
- Suggest improvements

## License
MIT License

Copyright (c) 2024 David Diaz

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Disclaimer
This tool is provided as-is. Always review code and follow your organization's security policies before use.

---
Made with ❤️ by David
