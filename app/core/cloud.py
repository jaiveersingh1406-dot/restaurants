import os
from io import BytesIO

import cloudinary
import cloudinary.uploader

IMAGE_FOLDER = os.environ.get("CLOUDINARY_FOLDER", "platia")


def _config():
    """Read Cloudinary credentials from the environment each call."""
    return {
        "cloud_name": os.environ.get("CLOUDINARY_CLOUD_NAME", "").strip(),
        "api_key": os.environ.get("CLOUDINARY_API_KEY", "").strip(),
        "api_secret": os.environ.get("CLOUDINARY_API_SECRET", "").strip(),
    }


def is_configured() -> bool:
    """Return True when real Cloudinary credentials have been provided."""
    cfg = _config()
    return bool(
        cfg["cloud_name"]
        and cfg["api_key"]
        and cfg["api_secret"]
        and cfg["api_secret"] != "PUT_YOUR_FULL_API_SECRET_HERE"
    )


def upload_image(file, public_id: str = None) -> dict:
    """Upload an image file (UploadFile) to Cloudinary and return the secure URL."""
    cfg = _config()
    if not is_configured():
        raise RuntimeError(
            "Cloudinary not configured. Set CLOUDINARY_CLOUD_NAME, "
            "CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET in the backend .env file."
        )

    cloudinary.config(
        cloud_name=cfg["cloud_name"],
        api_key=cfg["api_key"],
        api_secret=cfg["api_secret"],
    )

    content = file.file.read()

    options = {"folder": IMAGE_FOLDER}
    if public_id:
        options["public_id"] = public_id

    result = cloudinary.uploader.upload(BytesIO(content), **options)

    return {
        "url": result["secure_url"],
        "public_id": result.get("public_id"),
        "bytes": result.get("bytes"),
        "format": result.get("format"),
    }
