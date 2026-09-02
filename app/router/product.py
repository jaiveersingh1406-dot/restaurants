from fastapi import APIRouter, Depends, HTTPException
from app.schema.product import product
from app.service.product import get_product, get_products, create_product, update_product, delete_product   

router = APIRouter()

@router.get("/products")
def read_products():
    try:
        products = get_products()
        return products
    except HTTPException as exc:
        raise exc   
    
@router.get("/products/{product_id}")
def read_product(product_id: int):  
    try:
        product = get_product(product_id)
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except HTTPException as exc:
        raise exc
@router.get("/products")
def alldata():
    try:
        products = get_products()
        return products
    except HTTPException as exc:
        raise exc
    

@router.post("/products")
def create_new_product(product: product):
    try:
        new_product = create_product(product)
        return new_product
    except HTTPException as exc:
        raise exc


@router.put("/products/{product_id}")
def update_existing_product(product_id: int, product: product):
    try:
        updated_product = update_product(product_id, product)
        if updated_product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        return updated_product
    except HTTPException as exc:
        raise exc


@router.delete("/products/{product_id}")
def delete_existing_product(product_id: int):
    try:
        deleted_product = delete_product(product_id)
        if deleted_product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        return {"message": "Product deleted successfully"}
    except HTTPException as exc:
        raise exc

