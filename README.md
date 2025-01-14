# 🦊 TempFox

[![PyPI version](https://badge.fury.io/py/tempfox.svg)](https://badge.fury.io/py/tempfox)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)

## Description

TempFox is a streamlined Python tool that manages AWS credentials and automates CloudFox security checks. It elegantly handles both long-term (AKIA) and temporary (ASIA) AWS credentials.

```bash
  _____                   _____ 
 |_   _|__ _ __ ___  _ _|  ___|____  __
   | |/ _ \ '_ ` _ \| '_ \ |_ / _ \ \/ /
   | |  __/ | | | | | |_) |  _| (_) >  < 
   |_|\___|_| |_| |_| .__/|_|  \___/_/\_\
                     |_|                   
```

## Key Features

- 🔄 Automatic AWS CLI installation and version detection
- 🔑 Support for both AKIA (long-term) & ASIA (temporary) credentials
- ⏰ Token expiration handling with auto-renewal option
- ✅ Smart credential format validation and verification
- 🔍 Environment variable detection and reuse
- 🧪 AWS connection testing with detailed identity information
- 🦊 Seamless CloudFox integration for security checks

## Installation

There are several ways to install TempFox:

### Using pip (Recommended)
```bash
pip install tempfox
```

### From Source
```bash
git clone https://github.com/alfdav/tempfox.git
cd tempfox
pip install -e .
```

### Dependencies
- Python 3.6+
- boto3 >= 1.26.0
- AWS CLI (automatically installed if missing)

## Quick Start

1. Basic Usage:
```bash
tempfox
```

2. Using with AWS Access Key:
```bash
# Long-term credentials (AKIA)
export AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
export AWS_SECRET_ACCESS_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tempfox

# Temporary credentials (ASIA)
export AWS_ACCESS_KEY_ID=ASIAXXXXXXXXXXXXXXXX
export AWS_SECRET_ACCESS_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
export AWS_SESSION_TOKEN=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
tempfox
```

3. Auto-renewal Mode:
```bash
tempfox --auto-renew
```

4. Run CloudFox Security Checks:
```bash
# After credentials are configured
tempfox --cloudfox
```

5. Check Credential Status:
```bash
tempfox --status
```

## Prerequisites

- Python 3.6 or higher
- Linux operating system
- Internet connection
- Sudo privileges (for AWS CLI installation if needed)

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

THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER, AUTHORS, OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

USE OF THIS SOFTWARE IS ENTIRELY AT YOUR OWN RISK. THE AUTHORS ASSUME NO RESPONSIBILITY OR LIABILITY FOR ANY ERRORS OR OMISSIONS IN THE CONTENT OF THIS SOFTWARE. THE INFORMATION CONTAINED IN THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS WITH NO GUARANTEES OF COMPLETENESS, ACCURACY, USEFULNESS OR TIMELINESS.

By using this software, you acknowledge and agree that you are using it at your own risk and discretion. The authors shall not be held responsible for any security breaches, data loss, or any other damages resulting from the use of this software.

---
Made with ❤️ by David
