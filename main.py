from fastapi import FastAPI
from pydantic import BaseModel

class HelloRequest(BaseModel):
    name: str

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/hello")
def hello(body: HelloRequest):
    return {"message": f"Hello, {body.name}"}