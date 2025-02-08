from fastapi import FastAPI
from app.routes import users


app = FastAPI(title="E-Commerce API")

@app.get("/")
def root():
    return {"message": "E-Commerce API is running"}

app.include_router(users.router, prefix="/api")

if __name__ == "__main__":
    app.run()
