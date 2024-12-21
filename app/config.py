import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mysecretkey')  # Default to 'mysecretkey' if not set
    
    # Playwright browsers path (not required unless using a custom path)
    PLAYWRIGHT_BROWSERS_PATH = os.environ.get('PLAYWRIGHT_BROWSERS_PATH', None)  # Defaults to None if not set
