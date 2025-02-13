import random
import string
import os
import uuid
from typing import List
from fastapi import UploadFile, HTTPException

def generate_random_string(length: int = 12):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


async def upload_images(images: List[UploadFile], upload_dir: str = "uploads/products") -> List[str]:
    """
    Handles image uploads. Saves images locally for now.
    Can later be modified to upload to cloud storage (e.g., S3, Cloudinary).

    Args:
        images (List[UploadFile]): List of image files to upload.
        upload_dir (str): Directory to store uploaded images (local storage).

    Returns:
        List[str]: List of image URLs/paths.
    """
    if len(images) > 10:
        raise HTTPException(status_code=400, detail="You can upload a maximum of 10 images")

    os.makedirs(upload_dir, exist_ok=True)
    image_urls = []

    for image in images:
        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail=f"Invalid file type: {image.filename}")

        file_extension = image.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)

        # Simulate cloud upload here later
        with open(file_path, "wb") as f:
            f.write(await image.read())

        # This would later be a cloud URL (e.g., S3 URL)
        image_urls.append(f"/{file_path}")

    return image_urls