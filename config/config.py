import os
import dotenv

dotenv.load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    VECTOR_STORE_PATH = "vector_store"
    TASK_QUEUE_FILE = 'tasks_queue/tasks.json'
    GENERATED_CODE_PATH = 'generated_code'
    LOG_FILE = "logs/ai_agents.log"
    TEST_CODE_PATH = "test_code"
    QA_REPORT_PATH = "qa_reports"
    README_PATH = "readme"
    REFACTOR_PATH = "refactored_code"
    ARCHITECTURE_PATH = "ca_plan"