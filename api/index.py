import os
import sys

# This allows imports from your 'app' folder to work on Vercel
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")

# Import the FastAPI instance from your existing main file
# Assuming your main FastAPI variable is named 'app' inside app/main.py
from app.main import app