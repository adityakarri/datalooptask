import argparse
import subprocess
import time
import os
import signal
import psutil

# Global variables to store process information
processes = {}

def get_virtual_env_path():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    return os.path.join(parent_dir, 'venv', 'Scripts', 'python.exe')

VIRTUAL_ENV_PATH = get_virtual_env_path()

def start_game(pong_time_ms):
    print(f"Starting game with pong_time_ms={pong_time_ms}")
    global processes
    try:
        processes['server1'] = subprocess.Popen([VIRTUAL_ENV_PATH, "server1.py"])
        processes['server2'] = subprocess.Popen([VIRTUAL_ENV_PATH, "server2.py"])
        print(f"Started server1 with PID {processes['server1'].pid}")
        print(f"Started server2 with PID {processes['server2'].pid}")
    except Exception as e:
        print(f"Failed to start servers: {e}")
    
    time.sleep(2)  # Let servers initialize

def pause_game():
    
    # global processes
    for key, proc in processes.items():
        try:
            if proc.pid:
                p = psutil.Process(proc.pid)
                p.suspend()
                print(f"Paused {key} with PID {proc.pid}")
        except psutil.NoSuchProcess:
            print(f"Process {key} with PID {proc.pid} does not exist.")
        except psutil.AccessDenied:
            print(f"Access denied when trying to pause {key} with PID {proc.pid}.")
        except Exception as e:
            print(f"Failed to pause {key} with PID {proc.pid}: {e}")
    print("Pausing game")

def resume_game():
    print("Resuming game")
    global processes
    for key, proc in processes.items():
        try:
            if proc.pid:
                p = psutil.Process(proc.pid)
                p.resume()
                print(f"Resumed {key} with PID {proc.pid}")
        except psutil.NoSuchProcess:
            print(f"Process {key} with PID {proc.pid} does not exist.")
        except psutil.AccessDenied:
            print(f"Access denied when trying to resume {key} with PID {proc.pid}.")
        except Exception as e:
            print(f"Failed to resume {key} with PID {proc.pid}: {e}")

def stop_game():
    print("Stopping game")
    global processes
    for key, proc in processes.items():
        try:
            if proc.pid:
                proc.terminate()
                proc.wait()
                print(f"Terminated {key} with PID {proc.pid}")
        except psutil.NoSuchProcess:
            print(f"Process {key} with PID {proc.pid} does not exist.")
        except psutil.AccessDenied:
            print(f"Access denied when trying to terminate {key} with PID {proc.pid}.")
        except Exception as e:
            print(f"Failed to terminate {key} with PID {proc.pid}: {e}")

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
