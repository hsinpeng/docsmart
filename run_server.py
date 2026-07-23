from pydantic import BaseModel
from fastapi import FastAPI
import uvicorn

app = FastAPI()

class SimpleResponse(BaseModel):
    code: int
    data: str
    message: str
    is_finished: bool

@app.get("/", response_model=SimpleResponse)
def read_root():
    # Automatically validated, filtered, and converted to JSON
    response_json = {
        "code": 200,
        "data": "Hello, World!",
        "message": "OK",
        "is_finished": True
    }
    return response_json

if __name__ == "__main__":
    # Change "127.0.0.1" to "0.0.0.0"
    uvicorn.run("run_server:app", host="0.0.0.0", port=8000, reload=True)