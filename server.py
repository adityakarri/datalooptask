from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import asyncio
import uvicorn
import sys

app = FastAPI()

if len(sys.argv) > 2:
    server_name = sys.argv[1]
    PONG_TIME_MS = float(sys.argv[2])

else:
    server_name = "default_server"


if server_name == "server1":
    ping_url = "http://localhost:8001/ping"  # server1 pings server2
    initiate_ping = True  # Only server1 initiates the ping
elif server_name == "server2":
    ping_url = "http://localhost:8000/ping"  # server2 responds to server1
    initiate_ping = False  # server2 does not initiate ping
else:
    ping_url = ""
    initiate_ping = False  # Default server doesn't ping

# Configuration


# Events for pausing and resuming
pause_event = asyncio.Event()
pause_event.set()  # Start in "running" state


@app.get("/")
async def root():
    return {"message": f"Hello from {server_name}"}



@app.post("/ping")
async def ping():
    asyncio.create_task(ping_server())

@app.post("/pause")
async def pause():
    pause_event.clear()
    return {"message": "Server paused"}

@app.post("/resume")
async def resume():
    pause_event.set()
    return {"message": "Server resumed"}

async def ping_server():
    global PONG_TIME_MS

    await asyncio.sleep(PONG_TIME_MS / 1000)
    # Check if the server is paused
    await pause_event.wait()
    async with httpx.AsyncClient() as client:
        response = await client.post(ping_url)
        if response.status_code == 200:
            print("Received pong from " + server_name)
            

@app.on_event("startup")
async def startup_event():
    if initiate_ping:
        asyncio.create_task(ping_server())

if __name__ == "__main__":
    if server_name == "server1":
        uvicorn.run(app, host="0.0.0.0", port=8000)
    if server_name == "server2":
        uvicorn.run(app, host="0.0.0.0", port=8001)