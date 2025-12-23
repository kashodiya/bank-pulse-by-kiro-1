"""Configuration settings for BankPulse"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# AWS Configuration
AWS_PROFILE = os.getenv('AWS_DEFAULT_PROFILE', 'default')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
BEDROCK_MODEL_ID = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-sonnet-4-5-20250929-v1:0')

# Database Configuration
DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/bankpulse.db')

# H8 Data Configuration
H8_DATA_URL = os.getenv('H8_DATA_URL', 'https://www.federalreserve.gov/datadownload/Output.aspx?rel=H8&filetype=zip')
DATA_DIR = os.getenv('DATA_DIR', 'data')
