from openai import OpenAI
import os
from agents.base_agent import BaseAgent
from config.config import Config

class RefactorAgent(BaseAgent):
    def run_task(self, task):
        print(f"[RefactorAgent] run_task() called with task: {task}")

        file_name = task.get("input_file")
        if not file_name:
            print("[ERROR] No input_file specified in task.")
            return
        
        file_path = os.path.join(Config.GENERATED_CODE_PATH, file_name)
        if not os.path.exists(file_path):
            print(f"[ERROR] File {file_path} does not exist.")
            return
        
        with open(file_path, "r") as f:
            code_content = f.read()
        
        prompt = f"""
            You are a senior Python engineer with a deep understanding of code quality, performance optimization, and idiomatic Python. Your task is to refactor the provided Python code.

            **Please refactor the following Python code for improved readability, maintainability, and performance:**
            * **Readability:** Make the code easier to understand and follow. This includes:
                * Clearer variable and function names.
                * Consistent formatting and spacing (adhering to PEP 8).
                * Breaking down complex functions into smaller, more manageable ones.
                * Adding comments where the code's intent is not immediately obvious (but prioritize self-documenting code).
            * **Performance:** Optimize the code for efficiency where practical, considering:
                * Algorithmic improvements (e.g., choosing more efficient data structures or algorithms).
                * Minimizing unnecessary computations or I/O operations.
                * Avoiding redundant operations.
            * **Idiomatic Python Usage:** Ensure the code leverages Python's built-in features and conventions effectively, such as:
                * List comprehensions, dictionary comprehensions, generator expressions.
                * Context managers (`with` statements).
                * `enumerate()`, `zip()`, `map()`, `filter()`, `functools` tools.
                * Effective use of decorators and class methods where appropriate.
                * Avoiding "un-Pythonic" constructs.
            * **Maintainability:** Make the code easier to debug, modify, and extend in the future. This includes:
                * Reducing coupling and increasing cohesion.
                * Implementing clear module and package organization.
                * Improving error handling and validation.
                * Ensuring functions have a single responsibility.
            
            **Code:**
            {code_content}

            **Output:** Provide ONLY the improved Python code (no explanations, no prose, no markdown formatting outside of the code block).
        """
        
        try:
            client = OpenAI(api_key = Config.OPENAI_API_KEY)
            response = client.chat.completions.create(
                model = "gpt-4o-mini",
                messages = [{"role": "user", "content": prompt}],
                temperature = 0.2,
            )
            refactored_code = response.choices[0].message.content
            #print(f"[DEBUG] Refactored code: {refactored_code}")
            self.log(f"Generated refactored code: {refactored_code}")
        
        except Exception as e:
            print(f"[ERROR] Exception during OpenAI API call: {str(e)}")
            return
        
        #Save file
        os.makedirs(Config.REFACTOR_PATH, exist_ok = True)
        refactored_file_name = f"{os.path.splitext(file_name)[0]}_refactored.py"
        refactored_file_path = os.path.join(Config.REFACTOR_PATH, refactored_file_name)
        
        with open(refactored_file_path, "w") as f:
            f.write(refactored_code)
        
        print(f"[RefactorAgent] Refactored code saved to: {refactored_file_path}")