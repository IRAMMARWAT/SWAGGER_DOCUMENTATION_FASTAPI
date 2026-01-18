# test_simple.py - Minimal test
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def home():
    return {"message": "FastAPI is working!"}

@app.get("/test")
def test():
    return {"status": "ok", "docs": "Available at /docs"}

if __name__ == "__main__":
    print("Starting FastAPI server...")
    print("Open: http://127.0.0.1:8000")
    print("Docs: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)