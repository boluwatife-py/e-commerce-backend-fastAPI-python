from fastapi import FastAPI
from app.exceptions import validation_exception_handler, authentication_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="E-Commerce API")

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, authentication_exception_handler)


ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    
)
@app.get("/")
def root():
    return {"message": "E-Commerce API is running"}



from app.routes import auth, products

app.include_router(auth.router, prefix="/auth")
app.include_router(products.router, prefix="/products")
if __name__ == "__main__":
    app.run()
