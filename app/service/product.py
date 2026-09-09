import json

from app.db.db import get_connection
from app.schema.product import product
from fastapi import HTTPException


def _serialize_images(images):
    if images is None:
        return None
    if isinstance(images, str):
        return images
    if isinstance(images, (list, tuple)):
        return json.dumps([img for img in images if img])
    return json.dumps([str(images)])


def _parse_images(images):
    if not images:
        return None
    if isinstance(images, list):
        return images
    try:
        parsed = json.loads(images)
        return parsed if isinstance(parsed, list) else [str(images)]
    except (TypeError, ValueError):
        return [img for img in str(images).split(",") if img]


def _row_to_dict(row):
    data = dict(row)
    if "images" in data:
        data["images"] = _parse_images(data.get("images"))
    return data


def get_product(product_id: int):
    """Fetch a single product by ID"""
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute(
            "SELECT * FROM product WHERE id = %s",
            (product_id,)
        )
        
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        
        return _row_to_dict(result) if result else None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_products():
    """Fetch all product"""
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM product")
        results = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return [_row_to_dict(r) for r in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def create_product(product_data: product):
    """Create a new product"""
    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """INSERT INTO product
               (name, description, price, category, stock, status, image, rating, images)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
               RETURNING id""",
            (
                product_data.name,
                product_data.description,
                product_data.price,
                product_data.category,
                product_data.stock,
                product_data.status,
                product_data.image,
                product_data.rating,
                _serialize_images(product_data.images)
            )
        )

        connection.commit()
        product_id = cursor.fetchone()[0]

        cursor.close()
        connection.close()

        return get_product(product_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def update_product(product_id: int, product_data: product):
    """Update an existing product"""
    try:
        # Check if product exists
        existing = get_product(product_id)

        if not existing:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE product
            SET
                name = %s,
                description = %s,
                price = %s,
                category = %s,
                stock = %s,
                status = %s,
                image = %s,
                rating = %s,
                images = %s
            WHERE id = %s
            """,
            (
                product_data.name,
                product_data.description,
                product_data.price,
                product_data.category,
                product_data.stock,
                product_data.status,
                product_data.image,
                product_data.rating,
                _serialize_images(product_data.images),
                product_id
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return get_product(product_id)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
        

def delete_product(product_id: int):
    try:
        existing = get_product(product_id)
        if not existing:
            return None
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM product WHERE id = %s", (product_id,))
        connection.commit()
        cursor.close()
        connection.close()
        return existing
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    