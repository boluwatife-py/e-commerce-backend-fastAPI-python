from fastapi import FastAPI
from app.routes import users
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="E-Commerce API")
app.include_router(users.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "E-Commerce API is running"}


if __name__ == "__main__":
    app.run()
