from fastapi import FastAPI, Request
import requests
import asyncio

# Initialize FastAPI app
app = FastAPI()

# Global variables to manage game state
ping_url = None           # URL of the other server to send pings to
pong_time_ms = 1000       # Time interval between pings in milliseconds
is_paused = False         # Flag to determine if the game is paused

# Endpoint to handle incoming ping requests
@app.get("/ping")
async def ping(request: Request):
    if is_paused:
        # If the game is paused, inform the other server
        return {"status": "paused"}
    
    # If not paused, simply respond with a "pong"
    return {"response": "pong"}

# Endpoint to start the game
@app.post("/start")
async def start_game(pong_time: int, target_url: str):
    """
    Start the ping-pong game.

    Parameters:
    - pong_time: Time interval between pings (in milliseconds).
    - target_url: The URL of the server to ping.
    """
    global ping_url, pong_time_ms, is_paused
    ping_url = target_url
    pong_time_ms = pong_time
    is_paused = False

    # Start the first ping to the other server
    await send_ping()
    return {"status": "started"}

# Endpoint to pause the game
@app.post("/pause")
async def pause_game():
    global is_paused
    is_paused = True  # Set the pause flag to True
    return {"status": "paused"}

# Endpoint to resume the game from a paused state
@app.post("/resume")
async def resume_game():
    global is_paused
    is_paused = False  # Reset the pause flag
    await send_ping()  # Send a ping immediately after resuming
    return {"status": "resumed"}

# Endpoint to stop the game
@app.post("/stop")
async def stop_game():
    global is_paused, ping_url
    is_paused = True  # Set the pause flag to True
    ping_url = None   # Clear the target URL
    return {"status": "stopped"}

# Internal function to send a ping to the other server
async def send_ping():
    global ping_url, pong_time_ms
    if not ping_url or is_paused:
        # If no target URL is set or the game is paused, do nothing
        return

    # Wait for the specified pong time before sending the next ping
    await asyncio.sleep(pong_time_ms / 1000)

    try:
        # Send the ping request to the other server
        response = requests.get(f"{ping_url}/ping")
        print(f"Received: {response.json()}")

        # Recursively send another ping if the game is not paused
        if not is_paused:
            await send_ping()
    except requests.RequestException as e:
        print(f"Error pinging {ping_url}: {e}")
