from fastapi import FastAPI
from app.exceptions import validation_exception_handler, authentication_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException


app = FastAPI(title="E-Commerce API")

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, authentication_exception_handler)


@app.get("/")
def root():
    return {"message": "E-Commerce API is running"}



from app.routes import auth

app.include_router(auth.router, prefix="/auth")
if __name__ == "__main__":
    app.run()
