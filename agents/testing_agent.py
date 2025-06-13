from openai import OpenAI
import os
from agents.base_agent import BaseAgent
from config.config import Config

class TestingAgent(BaseAgent):
    def run_task(self, task):
        print(f"[TestingAgent] run_task() called with task: {task}")

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
        You are a senior Python testing engineer. Your primary responsibility is to ensure the robustness and correctness of the codebase by creating comprehensive unit tests. You will use `pytest` for all test generation.

        **Given the following Python code, generate a comprehensive unit test file:**
        {code_content}

        **Instructions:**
1.  **Scope:** Focus on generating unit tests for all functions within the provided `code_content`.
2.  **Test Cases:**
    * **Normal Cases:** Include tests for typical and expected inputs and behaviors.
    * **Edge Cases:** Identify and test boundary conditions, including but not limited to:
        * Empty inputs (e.g., empty strings, lists, dictionaries).
        * Null or `None` inputs.
        * Zero values.
        * Maximum/minimum allowable values.
        * Invalid data types.
        * Error conditions (e.g., file not found, division by zero, type errors).
    * **Negative Testing:** Test how the functions handle incorrect or unexpected inputs to ensure they fail gracefully or raise appropriate exceptions.
    * **Parameter Combinations:** If a function has multiple parameters, test various combinations of their values.
3.  **Assertions:** Use `pytest` assertions (e.g., `assert ...`, `pytest.raises(...)`) to verify expected outcomes.
4.  **Fixtures:** Use `pytest` fixtures if shared setup or teardown logic is required for multiple tests.
5.  **Test File Naming:** Name the test file `test_original_module_name.py` (inferring `original_module_name` from the context or assume a generic name like `test_module.py` if no module name can be inferred from `code_content`).
6.  **Code Coverage:** Aim for high code coverage, ensuring that as much of the provided `code_content` as possible is exercised by your tests.
7.  **No Explanations:** Provide ONLY valid Python test code. Do not include any additional explanations, prose, or markdown outside of the code block itself.

**Output:** Provide ONLY valid Python test code.
        
"""
        
        try:
            client = OpenAI(api_key = Config.OPENAI_API_KEY)

            #print(f"[DEBUG] Sending prompt to OpenAI...")
            response = client.chat.completions.create(
                model = "gpt-3.5-turbo",
                messages = [{"role": "user", "content": prompt}],
                temperature = 0.2,
            )
            test_code = response.choices[0].message.content.strip()
            #print(f"[DEBUG] Extracted test code: {test_code}")
            if test_code.startswith("```python"):
                test_code = test_code[len("```python"):].strip()
            if test_code.endswith("```"):
                test_code = test_code[:-3].strip()

            self.log(f"Generated test code: {test_code}")

        except Exception as e:
            print(f"[ERROR] Exception during OpenAI API call: {str(e)}")
            return
        
        #Save file
        os.makedirs(Config.TEST_CODE_PATH, exist_ok = True)
        test_file_name = f"test_{file_name}"
        test_file_path = os.path.join(Config.TEST_CODE_PATH, test_file_name)

        with open(test_file_path, "w") as f:
            f.write(test_code)
        
        print(f"[TestingAgent] Test file created: {test_file_path}")