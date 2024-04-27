import os

from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_dir, "..", "..", ".env.local")

load_dotenv(dotenv_path)
