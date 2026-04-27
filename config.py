import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

API_KEY = os.getenv("API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")