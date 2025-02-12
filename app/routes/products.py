from fastapi import APIRouter, Depends, HTTPException
from core.database import get_db
from app.models import Product, User, Category
from app.schemas import ProductResponse, ProductCreate, ReviewResponse
from core.auth import require_role
from typing import Annotated, Optional, List
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


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

        return products

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        print(f"Error retrieving products: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching products.")


@router.get("/{product_id}/", response_model=ProductResponse)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """Retrieve a single product by ID (with reviews & user ID)."""
    try:
        product = db.query(Product).filter(Product.product_id == product_id).first()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Ensure product.reviews exists before iterating
        reviews = []
        if hasattr(product, "reviews") and product.reviews:
            reviews = [
                ReviewResponse(id=rev.id, user_id=rev.user_id, rating=rev.rating, comment=rev.comment)
                for rev in product.reviews
            ]

        return ProductResponse(
            product_id=product.product_id,  # Ensure correct attribute
            name=product.name,
            description=product.description,
            price=product.price,
            stock_quantity=product.stock_quantity,
            category_id=product.category_id,
            brand=product.brand,
            images=product.images,
            seller_id=product.seller_id,
            created_at=product.created_at,
            updated_at=product.updated_at,
            reviews=reviews,
        )

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        print(f"Error retrieving product: {e}")  # Log error for debugging
        raise HTTPException(status_code=500, detail="An unexpected error occurred while retrieving the product.")


@router.post("/new/", response_model=ProductResponse)
async def create_product(
    product: ProductCreate,
    current_user: Annotated[User, Depends(require_role(['merchant']))],
    db: AsyncSession = Depends(get_db),
):
    try:
        if product.price <= 0:
            raise HTTPException(status_code=400, detail="Price must be greater than 0")
        if product.stock_quantity < 0:
            raise HTTPException(status_code=400, detail="Stock quantity cannot be negative")

        category = None
        if product.category_id != None:
            category = db.query(Category).filter(Category.category_id == product.category_id).first()
            if not category:
                raise HTTPException(status_code=404, detail="Category not found")

        new_product = Product(
            name=product.name,
            description=product.description,
            price=product.price,
            stock_quantity=product.stock_quantity,
            category_id=product.category_id if category else None,
            seller_id=current_user.user_id,
            brand=product.brand,
            images=product.images
        )

        db.add(new_product)
        db.commit()
        db.refresh(new_product)

        return new_product
    
    except HTTPException:
        raise
    
    except IntegrityError:
        db.rollback()
        print(e)
        raise HTTPException(status_code=400, detail="Database integrity error. Check your inputs.")

    except SQLAlchemyError as e:
        db.rollback()
        print(e)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    except Exception as e:
        db.rollback()
        print(e)
        raise HTTPException(status_code=500, detail=f"An unexpected error occured, please try again later")


@router.get("/{product_id}/edit/", response_model=ProductCreate)
async def get_product_for_edit(
    product_id: int, 
    current_user: Annotated[User, Depends(require_role(['merchant']))], 
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch product details for editing. 
    Only the product owner can retrieve it.
    """
    try:
        product = db.query(Product).filter(Product.product_id == product_id).first()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        if product.seller_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="You do not have permission to edit this product")

        return ProductCreate(
            name=product.name,
            description=product.description,
            price=product.price,
            stock_quantity=product.stock_quantity,
            category_id=product.category_id,
            brand=product.brand,
            images=product.images
        )

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="An unexpected error occurred while retrieving the product.")


@router.put("/{product_id}/edit", response_model=ProductResponse)
async def update_product(
    product_id: int, 
    product_data: ProductCreate,
    current_user: Annotated[User, Depends(require_role(['merchant']))], 
    db: AsyncSession = Depends(get_db)
):
    """
    Allows only the product owner (seller) to update the product.
    Ensures price and stock_quantity are valid.
    """
    try:
        product = db.query(Product).filter(Product.product_id == product_id).first()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        
        if product.seller_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="You do not have permission to edit this product")

        
        if product_data.price is not None and product_data.price <= 0:
            raise HTTPException(status_code=400, detail="Price must be greater than 0")
        
        if product_data.stock_quantity is not None and product_data.stock_quantity < 0:
            raise HTTPException(status_code=400, detail="Stock quantity cannot be negative")
        
        category = None
        if product_data.category_id != None:
            category = db.query(Category).filter(Category.category_id == product_data.category_id).first()
            if not category:
                raise HTTPException(status_code=404, detail="Category not found")
        
        for field in product_data.__dict__:
            value = getattr(product_data, field)
            if value is not None:
                setattr(product, field, value)

        db.commit()
        db.refresh(product)

        return product

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        print(f"Error updating product: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while updating the product.")


@router.delete("/{product_id}/")
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

