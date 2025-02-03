from fastapi import FastAPI

app = FastAPI(title="E-Commerce API")

@app.get("/")
def root():
    return {"message": "E-Commerce API is running"}
