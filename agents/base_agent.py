from abc import ABC, abstractmethod
import logging
from config.config import Config

logging.basicConfig(
    filename = Config.LOG_FILE,
    level = logging.INFO
)

class BaseAgent(ABC):
    def __init__(self, name, vector_store):
        self.name = name
        self.vector_store = vector_store
    
    @abstractmethod
    def run_task(self, task):
        pass

    def log(self, msg):
        print(f"[{self.name}] {msg}")
        logging.info(f"[{self.name}] {msg}")