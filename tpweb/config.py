
from dotenv import load_dotenv
import os

def has_config():
    # Check if the .env file exists
    return os.path.exists('.env')

def load_config():
    # Check if the .env file exists
    if not has_config():
        return
    
    load_dotenv()

def get_config():
    obj = {
        'ROOT_DIR': os.getenv('ROOT_DIR'),
        'SERVER_TYPE': os.getenv('SERVER_TYPE'),
        'IPV6': os.getenv('IPV6'),
        'IPV4': os.getenv('IPV4')
    }

    if obj['SERVER_TYPE'] == 'worker':
        obj['MASTER_IP'] = os.getenv('MASTER_IP')
        obj['MASTER_KEY'] = os.getenv('MASTER_KEY')

    return obj

def get_root_dir():
    return os.getenv('ROOT_DIR') + '/'