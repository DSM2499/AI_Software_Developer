import json
from config.config import Config

def load_tasks():
    with open(Config.TASK_QUEUE_FILE, 'r') as file:
        return json.load(file)
    
def save_tasks(tasks):
    with open(Config.TASK_QUEUE_FILE, 'w') as file:
        json.dump(tasks, file, indent = 2)
