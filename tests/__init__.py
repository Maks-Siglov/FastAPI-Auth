import os
import sys

from dotenv import load_dotenv

SRC_DIR = os.path.join(os.path.dirname(__file__), "../src")
sys.path.append(os.path.abspath(SRC_DIR))

load_dotenv(".env.test")

assert os.getenv("ENV") == "TEST"
