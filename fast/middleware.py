import time
from fastapi import FastAPI, Request

app = FastAPI()

@app.middleware("http")
async def my_middleware(req: Request, call_next):
    # Pre-processing logic
    print(f"Request URL: {req.url}")

    response = await call_next(req)
    
    # Post-processing logic
    print("Response Send")
    
    return response

@app.middleware("http")
async def add_process_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"Path: {request.url.path} | Process time: {process_time} seconds")
    return response