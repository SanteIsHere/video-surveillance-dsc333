"""
Name: main.py
Author: Asante Frye
"""

# Import required libraries
import cv2  # Computer Vision library for camera capture analysis
from dotenv import (
    load_dotenv,
)  # Import function to load envionment variables from env file
from time import sleep  # To establish delays between captures
import os  # To read environment variables
from EnvException import EnvException

# Load environment variables
env_found: bool = load_dotenv()

# Attempt to Read API key
try:
    if not env_found or not os.environ.get("API_KEY"):
        raise EnvException(
            "Could not load the environment... "
            "Please ensure a valid '.env' file is present "
            " with your GCP API_KEY defined"
        )
    else:
        API_KEY = os.environ.get("API_KEY")  # Get the user's API_KEY
except EnvException as e:
    print(e)
