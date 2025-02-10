from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Custom exception handler for validation errors
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])  # Extract field name
        message = error["msg"]
        errors.append({"field": field, "message": message})
    
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation Error", "errors": errors},
    )

# Custom exception handler for authentication errors
async def authentication_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": "Authentication failed", "message": exc.detail},
    )

