from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.cloud import is_configured, upload_image
from app.db.db import get_connection

router = APIRouter()


@router.post("/content/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload an image to Cloudinary and return its secure URL."""
    try:
        if not is_configured():
            raise HTTPException(
                status_code=503,
                detail="Cloudinary not configured. Set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET.",
            )

        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")

        result = upload_image(file)

        return {
            "url": result["url"],
            "public_id": result["public_id"],
            "bytes": result["bytes"],
            "format": result["format"],
            "filename": file.filename,
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/content/reviews")
def get_reviews():
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM reviews ORDER BY id ASC")
        rows = cursor.fetchall()
        cursor.close()
        connection.close()
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/content/gallery")
def get_gallery():
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT image_url FROM gallery_images ORDER BY id ASC")
        rows = cursor.fetchall()
        images = [row["image_url"] for row in rows]
        cursor.close()
        connection.close()
        return images
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/content/messages")
def get_messages():
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, name, email, subject, message, sent_at FROM messages ORDER BY id DESC"
        )
        rows = cursor.fetchall()
        cursor.close()
        connection.close()
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/content/messages")
def create_message(payload: dict):
    try:
        name = (payload.get("name") or "").strip()
        email = (payload.get("email") or "").strip()
        subject = (payload.get("subject") or "").strip()
        message = (payload.get("message") or "").strip()

        if not name or not email or not message:
            raise HTTPException(status_code=400, detail="Name, email and message are required")

        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """INSERT INTO messages (name, email, subject, message)
               VALUES (%s, %s, %s, %s)
               RETURNING id""",
            (name, email, subject or None, message),
        )
        connection.commit()
        message_id = cursor.fetchone()[0]
        cursor.close()
        connection.close()
        return {"message": "Message sent successfully", "id": message_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
