import os
import sys
from pathlib import Path

# Ensure root directory is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Mark serverless execution environment
os.environ["VERCEL"] = "1"

# Import FastAPI app from server.py
from server import app
