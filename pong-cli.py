import argparse
import subprocess
import time
import os
import requests
import psutil

# Path to store the PIDs
PID_FILE_PATH = "server_pids.txt"

def get_virtual_env_path():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    return os.path.join(parent_dir, 'venv', 'Scripts', 'python.exe')

VIRTUAL_ENV_PATH = get_virtual_env_path()

def write_pids_to_file(pids):
    with open(PID_FILE_PATH, "w") as f:
        for key, pid in pids.items():
            f.write(f"{key}:{pid}\n")

def read_pids_from_file():
    if not os.path.exists(PID_FILE_PATH):
        return {}
    
    pids = {}
    with open(PID_FILE_PATH, "r") as f:
        for line in f:
            key, pid = line.strip().split(":")
            pids[key] = int(pid)
    return pids

def start_game(pong_time_ms):
    print(f"Starting game with pong_time_ms={pong_time_ms}")
    processes = {}
    try:
        processes['server2'] = subprocess.Popen([VIRTUAL_ENV_PATH, "server.py", "server2", str(pong_time_ms)])
        processes['server1'] = subprocess.Popen([VIRTUAL_ENV_PATH, "server.py", "server1", str(pong_time_ms)])
        print(f"Started server1 with PID {processes['server1'].pid}")
        print(f"Started server2 with PID {processes['server2'].pid}")
        write_pids_to_file({key: proc.pid for key, proc in processes.items()})
    except Exception as e:
        print(f"Failed to start servers: {e}")
    
    time.sleep(2)  # Let servers initialize

def pause_game():
    print("Pausing game")
    try:
        response1 = requests.post("http://localhost:8000/pause")
        response2 = requests.post("http://localhost:8001/pause")
        if response1.status_code == 200:
            print("Server1 paused")
        else:
            print(f"Failed to pause Server1: {response1.text}")
        
        if response2.status_code == 200:
            print("Server2 paused")
        else:
            print(f"Failed to pause Server2: {response2.text}")
    except Exception as e:
        print(f"Failed to pause servers: {e}")

def resume_game():
    print("Resuming game")
    try:
        response1 = requests.post("http://localhost:8000/resume")
        response2 = requests.post("http://localhost:8001/resume")
        if response1.status_code == 200:
            print("Server1 resumed")
        else:
            print(f"Failed to resume Server1: {response1.text}")
        
        if response2.status_code == 200:
            print("Server2 resumed")
        else:
            print(f"Failed to resume Server2: {response2.text}")
    except Exception as e:
        print(f"Failed to resume servers: {e}")

def stop_game():
    print("Stopping game")
    pids = read_pids_from_file()
    for key, pid in pids.items():
        try:
            p = psutil.Process(pid)
            p.terminate()
            p.wait()
            print(f"Terminated {key} with PID {pid}")
        except psutil.NoSuchProcess:
            print(f"Process {key} with PID {pid} does not exist.")
        except psutil.AccessDenied:
            print(f"Access denied when trying to terminate {key} with PID {pid}.")
        except Exception as e:
            print(f"Failed to terminate {key} with PID {pid}: {e}")
    
    # Clean up PID file after stopping
    if os.path.exists(PID_FILE_PATH):
        os.remove(PID_FILE_PATH)

def main():
    parser = argparse.ArgumentParser(description="Control the Pong game between two servers.")
    parser.add_argument("command", choices=["start", "pause", "resume", "stop"], help="Command to control the game.")
    parser.add_argument("param", type=int, nargs="?", help="Parameter for the start command.")

    args = parser.parse_args()

    if args.command == "start":
        if args.param is None:
            print("Error: 'start' command requires a pong_time_ms parameter.")
            return
        start_game(args.param)
    elif args.command == "pause":
        pause_game()
    elif args.command == "resume":
        resume_game()
    elif args.command == "stop":
        stop_game()

if __name__ == "__main__":
    main()
