import os
from pathlib import Path
import torch
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = Path(os.getenv('IMAGE_DATA_DIR', BASE_DIR / 'data'))
MODEL_DIR = BASE_DIR / 'models'

# Model configuration
MODEL_NAME = os.getenv('MODEL_NAME', 'openai/clip-vit-base-patch32')
DEVICE = os.getenv('DEVICE', 'cuda' if torch.cuda.is_available() else 'cpu')

# Image processing
IMAGE_SIZE = int(os.getenv('IMAGE_SIZE', '224'))
BATCH_SIZE = int(os.getenv('BATCH_SIZE', '32'))

# Retrieval configuration
TOP_K = int(os.getenv('TOP_K', '5'))

# API Configuration
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', '8000'))
CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:8000').split(',')

# Create directories if they don't exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)
