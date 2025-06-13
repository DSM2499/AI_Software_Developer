from openai import OpenAI
import os
from agents.base_agent import BaseAgent
from config.config import Config
from shared.task_manager import TaskManager

class CodeArchitectAgent(BaseAgent):
    def __init__(self, name, vector_store):
        super().__init__(name, vector_store)
        self.task_manager = TaskManager()

    def run_task(self, task):
        print(f"[CodeArchitectAgent] run_task() called with task: {task}")

        prompt = f"""
        You are a senior software architect.  
For the following software feature, produce an architecture plan in this exact format:

# Architecture Plan

## Modules and Files
Provide at least 3 Python modules.  
For each module, output:

- module_name.py: short description

Example:

- csv_reader.py: reads CSV files and returns list of records
- data_transformer.py: applies transformations to data
- db_loader.py: loads data into PostgreSQL

## Dependencies Between Modules
- ...

## Key Classes and Functions
- module_name.py:
    - class ClassName:
        - method_name()
    - function_name()

## Suggested File Structure
- /project_root
    - /module1
        - module1.py
    - /module2
        - module2.py
    - main.py

**VERY IMPORTANT:**  
You must include exactly these section headers:

- `## Modules and Files`
- `## Dependencies Between Modules`
- `## Key Classes and Functions`
- `## Suggested File Structure`

Do not skip any section.  
Always include **Modules and Files** with at least 3 modules.

Feature:

{task['description']}
        """

        try:
            #print(f"[DEBUG] Sending prompt to OpenAI...")
            client = OpenAI(api_key = Config.OPENAI_API_KEY)
            response = client.chat.completions.create(
                model = "gpt-4o-mini",
                messages = [{"role": "user", "content": prompt}],
                temperature = 0.2,
            )
            architecture_plan = response.choices[0].message.content
            #print(f"[DEBUG] Architecture plan: {architecture_plan}")
            self.log(f"Generated architecture plan: {architecture_plan}")

        except Exception as e:
            print(f"[ERROR] Exception during OpenAI API call: {str(e)}")
            return
        
        #Save file
        os.makedirs(Config.ARCHITECTURE_PATH, exist_ok = True)
        architecture_file_name = f"{task.get('file_name')}.md"
        architecture_file_path = os.path.join(Config.ARCHITECTURE_PATH, architecture_file_name)

        print(f"[DEBUG] Type of plan: {type(architecture_plan)}")
        if isinstance(architecture_plan, list):
            print("[WARN] Plan was a list, converting to string.")
            architecture_plan = "\n".join(architecture_plan)

        with open(architecture_file_path, "w") as f:
            f.write(architecture_plan)
        
        print("[CodeArchitectAgent] Architecture plan created.")
        
        print(f"[CodeArchitectAgent] Architecture plan saved to: {architecture_file_path}")
        return [architecture_file_path]