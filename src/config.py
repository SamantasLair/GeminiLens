import os
from dotenv import load_dotenv
import sys

# Load .env file
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TESSERACT_CMD = os.getenv("TESSERACT_CMD")

if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY not found in .env file.")

if not TESSERACT_CMD:
    # Fallback to default if not set
    TESSERACT_CMD = r"./tesseract/tesseract.exe"

# Normalize path if relative
if not os.path.isabs(TESSERACT_CMD):
    TESSERACT_CMD = os.path.abspath(os.path.join(os.getcwd(), TESSERACT_CMD))
