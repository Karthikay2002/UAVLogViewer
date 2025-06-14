import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(__file__)
load_dotenv(os.path.join(BASE_DIR, ".env"))

UPLOAD_DIR = os.path.join(BASE_DIR, "uploaded_files")
os.makedirs(UPLOAD_DIR, exist_ok=True) 