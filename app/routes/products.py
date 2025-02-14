from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from core.database import get_db
from app.models import Product, User, Category, ProductImages
from app.schemas import ProductResponse, ProductCreate, ReviewResponse
from core.auth import require_role
from typing import Annotated, Optional, List
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload


router = APIRouter()


@router.get("/", response_model=List[ProductResponse])
async def get_products(
    db: AsyncSession = Depends(get_db),
    category_name: Optional[str] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = 10,
    offset: int = 0
):

    try:
        if limit <= 0 or limit > 100:
            raise HTTPException(status_code=400, detail="Limit must be between 1 and 100")
        if offset < 0:
            raise HTTPException(status_code=400, detail="Offset must be 0 or greater")

        query = db.query(Product)
        # query.filter(Product.status == 'published')
        if category_name:
            query = query.filter(Product.category_name == category_name)
        if brand:
            query = query.filter(Product.brand == brand)
        if min_price is not None:
            if min_price < 0:
                raise HTTPException(status_code=400, detail="Minimum price must be non-negative")
            query = query.filter(Product.price >= min_price)
        if max_price is not None:
            if max_price < 0:
                raise HTTPException(status_code=400, detail="Maximum price must be non-negative")
            query = query.filter(Product.price <= max_price)

        
        products = query.offset(offset).limit(limit).all()

        if not products:
            raise HTTPException(status_code=404, detail="No products found with the given filters")

        return ProductResponse.model_validate(products)

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        print(f"Error retrieving products: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching products.")


@router.get("/{product_id}/product/view/", response_model=ProductResponse)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """Retrieve a single product by ID (with reviews & user ID)."""
    product = db.get(Product, product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return ProductResponse.model_validate(product)

@router.get('/create/product/', response_model=int)
async def create_product(
    current_user: Annotated[User, Depends(require_role(['merchant']))],
    db: AsyncSession = Depends(get_db)
) -> int:
    try:
        new_product = Product(
            seller=current_user
        )
        
        print(new_product.seller_id)
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        
        return new_product.product_id
        
    except HTTPException:
        raise

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    except Exception as e:
        db.rollback()
        print(e)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@router.put("/edit/{product_id}/product/", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product: ProductCreate,
    current_user: Annotated[User, Depends(require_role(['merchant']))],
    db: AsyncSession = Depends(get_db),
):
    try:
        existing_product = db.get(Product, product_id)

        if not existing_product:
            raise HTTPException(status_code=404, detail="Product not found")

        if existing_product.seller_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="You do not have permission to edit this product")

        # Updating fields if provided
        if product.name is not None:
            existing_product.name = product.name
        if product.description is not None:
            existing_product.description = product.description
        if product.price is not None:
            if product.price <= 0:
                raise HTTPException(status_code=400, detail="Price must be greater than 0")
            existing_product.price = product.price
        if product.stock_quantity is not None:
            if product.stock_quantity < 0:
                raise HTTPException(status_code=400, detail="Stock quantity cannot be negative")
            existing_product.stock_quantity = product.stock_quantity
        if product.brand is not None:
            existing_product.brand = product.brand

        if product.category_id is not None:
            category = db.get(Category, product.category_id)
            if not category:
                raise HTTPException(status_code=404, detail="Category not found")
            existing_product.category_id = product.category_id

        
        if hasattr(product, 'status') and product.status in ['draft', 'published']:
            existing_product.status = product.status

            if product.status == 'published':
                if not all([existing_product.name, existing_product.price, existing_product.stock_quantity]):
                    raise HTTPException(
                        status_code=400,
                        detail="Cannot publish a product with missing name, price, or stock_quantity",
                    )

        db.commit()
        db.refresh(existing_product)

        return existing_product

    except HTTPException:
        raise

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    except Exception as e:
        db.rollback()
        print(e)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@router.delete("/delete/{product_id}/product/")
async def delete_product(
    product_id: int, 
    current_user: Annotated[User, Depends(require_role(['merchant']))], 
    db: AsyncSession = Depends(get_db)
):
    """
    Allows only the product owner (seller) to delete the product.
    Ensures proper error handling.
    """
    try:
        product = db.query(Product).filter(Product.product_id == product_id).first()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        
        if product.seller_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="You do not have permission to delete this product")

        db.delete(product)
        db.commit()
        return {"message": "Product deleted successfully"}

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        db.rollback()
        print(f"Error deleting product: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while deleting the product.")

@router.post("/upload/image/product")
async def upload_product_image(
    current_user: Annotated[User, Depends(require_role(['merchant']))],
    product_id: int = Form(...),
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    try:
        product = db.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        if product.seller_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="You do not have permission to this product")

        # Upload image to your storage system and get URL
        # Simulating it here:
        image_url = f"https://example.com/uploads/{image.filename}"

        new_image = ProductImages(
            product_id=product.product_id,
            image_url=image_url
        )

        db.add(new_image)
        db.commit()
        db.refresh(new_image)

        return {"image_id": new_image.id, "image_url": new_image.image_url, 'product':product.product_id}

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")