from openai import OpenAI
import os
from agents.base_agent import BaseAgent
from config.config import Config
from shared.task_manager import TaskManager

class QAAgent(BaseAgent):
    def __init__(self, name, vector_store):
        super().__init__(name, vector_store)
        self.task_manager = TaskManager()

    def run_task(self, task):
        print(f"[QAAgent] run_task() called with task: {task}")

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
            You are an expert software quality engineer with a strong focus on Python development. 
            You are tasked with performing a thorough review of the provided Python code for quality, correctness, style, maintainability, and security. 
            You will leverage static analysis tools and your expertise to identify areas for improvement.

            **Code to review:**
            {code_content}

            **QA Report Sections:**
            ## 1. Summary
            * Provide a high-level overview of the code's purpose and your overall assessment of its quality.
            * Highlight the most critical findings.

            ## 2. Code Readability & Style (PEP8 Adherence)
            * **Identify and list specific PEP8 violations:** (e.g., line length, naming conventions, inconsistent spacing).
            * **Comment on code clarity:** Is the logic easy to follow? Are there any overly complex sections?
            * **Suggest style improvements:** (e.g., using `autopep8` for auto-formatting ).

            ## 3. Documentation & Docstrings
            * **Assess the presence and quality of docstrings:** Are all functions, classes, and modules appropriately documented?
            * **Evaluate inline comments:** Are comments clear, concise, and helpful? Are there any magic numbers or unclear logic that needs commenting?
            * **Suggest improvements for documentation:** (e.g., adding missing docstrings, improving clarity, ensuring examples where beneficial).

            ## 4. Error Handling & Edge Cases
            * **Analyze error handling mechanisms:** Are `try-except` blocks used effectively? Are specific exceptions caught, or are broad exceptions being used?
            * **Identify unhandled potential errors:** Are there any operations that could fail unexpectedly without proper handling?
            * **Review handling of edge cases:** How does the code behave with:
            * Empty inputs (e.g., `""`, `[]`).
            * `None` values.
            * Zero or negative numbers where positive are expected.
            * Invalid data types.
            * **Suggest improvements for robustness:** (e.g., adding specific exception handling, input validation).

            ## 5. Potential Bugs
            * **Identify any logic errors or potential defects:** (e.g., off-by-one errors, incorrect loop conditions, race conditions if applicable).
            * **Highlight security vulnerabilities:** (e.g., injection flaws, insecure deserialization, weak cryptographic practices, exposed sensitive information based on `Bandit` insights).
            * **Explain the potential impact of each bug.**

            ## 6. Test Coverage Suggestions
            * **Identify areas of the code that appear to have insufficient test coverage.**
            * **Suggest specific test cases that should be added** by the Testing Agent to cover identified gaps, especially for edge cases and potential bugs.
            * **Reference the need for comprehensive unit tests** that cover all function paths and error conditions.

           ## 7. Suggestions for Improvement
            * **Provide actionable recommendations for code refactoring:** (e.g., breaking down large functions, improving module organization).
            * **Suggest performance optimizations** if any obvious bottlenecks are present.
            * **Recommend design pattern adherence** if applicable (e.g., factory, singleton, observer).
            * **Propose general best practices** for maintainability and scalability.
            * **Note any automated fixes that could be applied** (e.g., by `autopep8` ).
            * **Suggest creating remediation tasks** if the issues are complex or require significant effort.
            
"""
        
        try:
            #print(f"[DEBUG] Sending prompt to OpenAI...")
            client = OpenAI(api_key = Config.OPENAI_API_KEY)

            response = client.chat.completions.create(
                model = "gpt-3.5-turbo",
                messages = [{"role": "user", "content": prompt}],
                temperature = 0.3,
            )
            #print(f"[DEBUG] API raw response: {response}")
            self.log(f"Generated QA report: {response}")

            qa_report = response.choices[0].message.content
            #print(f"[DEBUG] Extracted QA report: {qa_report}")
        
        except Exception as e:
            print(f"[ERROR] Exception during QAAgent API call: {str(e)}")
            return
        
        os.makedirs(Config.QA_REPORT_PATH, exist_ok = True)
        qa_file_name = f"{os.path.splitext(file_name)[0]}_qa_report.md"
        qa_file_path = os.path.join(Config.QA_REPORT_PATH, qa_file_name)
        
        with open(qa_file_path, "w") as f:
            f.write(qa_report)
        
        new_refactor_task = {
            "agent": "RefactoringAgent",
            "input_file": task.get("input_file"),
            "completed": False
        }
        self.task_manager.add_task(new_refactor_task)    
        
        print(f"[QAAgent] QA report created: {qa_file_path}")