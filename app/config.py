import os
from dotenv import load_dotenv


load_dotenv()

class Config:
    
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mysecretkey')  
    

    PLAYWRIGHT_BROWSERS_PATH = os.environ.get('PLAYWRIGHT_BROWSERS_PATH', None)  # Default is set to none rn!
