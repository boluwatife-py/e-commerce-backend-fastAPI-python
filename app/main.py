from fastapi import FastAPI
from app.routes import auth


app = FastAPI(title="E-Commerce API")

@app.get("/")
def root():
    return {"message": "E-Commerce API is running"}

app.include_router(auth.router, prefix="/auth")

if __name__ == "__main__":
    app.run()
