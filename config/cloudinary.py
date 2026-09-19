import cloudinary
import os
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name = os.getenv("cloudinary_name"),
    api_key = os.getenv("cloudinary_key"),
    api_secret = os.getenv("cloudinary_secret")
)