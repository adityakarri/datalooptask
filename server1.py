# server1.py

from fastapi import FastAPI
from pydantic import BaseModel
import httpx
import asyncio
import uvicorn

app = FastAPI()

# Configuration
PONG_TIME_MS = 1000  # Default pong time in milliseconds
ping_url = "http://localhost:8001/ping"  # Change this to server2 URL for server1

@app.post("/ping")
async def ping():
    return {"message": "pong"}

async def ping_server():
    global PONG_TIME_MS
    while True:
        await asyncio.sleep(PONG_TIME_MS / 1000)
        async with httpx.AsyncClient() as client:
            response = await client.post(ping_url)
            if response.status_code == 200:
                print("Received pong from server2")

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(ping_server())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
