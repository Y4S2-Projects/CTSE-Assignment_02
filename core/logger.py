import datetime
import os

LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs.txt")

def log(agent_name: str, message: str) -> None:
    """Logs a message from an agent to the console and a file.
    
    Args:
        agent_name (str): The name of the agent generating the log.
        message (str): The message to log.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{agent_name}]: {message}"
    
    # Print to console
    print(log_entry)
    
    # Save to logs.txt
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
    except Exception as e:
        print(f"Failed to write to log file: {e}")
