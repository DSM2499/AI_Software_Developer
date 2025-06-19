print(">>> LOADING CodingAgent module...")

from openai import OpenAI
import os
from agents.base_agent import BaseAgent
from config.config import Config
from shared.git_utils import commit_generated_code
from shared.memory_graph import MemoryGraph



class CodingAgent(BaseAgent):
    def __init__(self, name, vector_store):
        super().__init__(name, vector_store)
        self.memory = MemoryGraph(vector_store)

    def run_task(self, task):
        print(f"[CodingAgent] run_task() called with task: {task['description']}")

        # Retrieve relevant memories for additional context
        memory_snippets = []
        for node_id, text, _ in self.memory.query(task["description"], k=3):
            memory_snippets.append(text)
        memory_context = "\n".join(memory_snippets)

        #print(f"[DEBUG] Before building prompt...")

        prompt = f"""
        You are a senior software engineer and an AI pair programmer. Your task is to implement the following feature, focusing on writing clean, efficient, and well-tested code.
        **Feature Description:**
        {task['description']}

        **Lifelong Context:**
        {memory_context}

        **Context and Requirements:**
        * **Project Goal:** (Provide a brief overview of the project's current state and immediate goals related to this task. This information would ideally come from the Project Manager Agent or the RAG system.)
        * **Architectural Guidelines:** (Retrieve relevant architectural patterns or design decisions from the knowledge base using RAG. Example: "Retrieve design documents for [module X] and adhere to its principles.")
        * **Existing Codebase:** (If applicable, provide context about where this new code should integrate. Example: "Review the 'src/utils' directory for existing helper functions related to this task.")
        * **Output:** Your primary output will be functional Python code that implements the feature. This includes creating new files as necessary, generating appropriate function bodies, and ensuring all code is well-commented and includes docstrings.
        * **Version Control:** After completing the code, you will automatically create a new commit with a clear and concise commit message that reflects the implemented feature and its status. Push your changes to the repository.

        **Instructions and Best Practices:**
        1.  **Knowledge Retrieval (RAG):** Before writing any code, actively query the knowledge base (`knowledge_base.search(query)`) for relevant information. Focus your queries on:
            * "Similar code examples for [task related keywords]"
            * "API specifications for [relevant external services/libraries]"
            * "Project design documents related to [module/feature]"
            * "Best practices for [programming language/framework]"
            * Integrate this retrieved context into your coding process to reduce hallucinations and ensure accuracy.

        2.  **Code Generation:**
            * Generate complete function bodies from provided stubs or comments.
            * Prioritize clear, readable, and maintainable code.
            * Consider edge cases and potential error handling.

        3.  **Quality Assurance:**
            * Write code with testability in mind, even though the Testing Agent will generate the actual tests.
            * Anticipate static analysis checks (linting, style, security) by adhering to established coding standards (e.g., PEP 8 for Python).
            * If you receive feedback from the QA Agent regarding issues, analyze the feedback and propose fixes or create a new sub-task for remediation.

        4.  **Collaboration:**
            * Your work will be reviewed by other agents (e.g., Testing Agent, QA Agent). Ensure your outputs are clear and easily understood by them.
        
        5.  **Efficiency:**
            * Leverage the speed of the LLM for rapid code generation and completion.
            * Consider optimal algorithms and data structures where performance is critical.
        
        **Example of how to structure your output (adjust as needed):**

        ```python
        # new_feature_module.py

        
        Docstring explaining the purpose of this module.
        

        # Context from RAG: 
        # - Similar code snippet found for X: `def example_func(): ...`
        # - API spec for Y: `endpoint: /api/y_service`

        def implement_feature_X(input_data):
            
            Implements feature X based on the task description.
            
            Args:
                input_data: Description of input.
                Returns:
            Description of output.
    
            # Your generated code goes here 
            # Make sure to utilize context from knowledge_base.search() 

            return result
        # Additional functions or classes as needed
        
        """
        
        #print(f"[DEBUG] After building prompt...")
        #self.log(f"Sending prompt to OpenAI...")
        try:
            client = OpenAI(api_key = Config.OPENAI_API_KEY)
            #print(f"[DEBUG] Client created")
            response = client.chat.completions.create(
                model = "gpt-4o-mini",
                messages = [{"role": "user", "content": prompt}],
                temperature = 0.2,
            )
            #print(f"[DEBUG] API raw response: {response}")
            code = response.choices[0].message.content
            #print(f"[DEBUG] Extracted code: {code}")
            self.log(f"Generated code: {code}")

        except Exception as e:
            self.log(f"Exception during OpenAI API call: {str(e)}")
            print(f"[ERROR] Exception during OpenAI API call: {str(e)}")
            return

        #Save file
        file_name = task.get("output_file", "generated_code.py")
        file_path = os.path.join(Config.GENERATED_CODE_PATH, file_name)

        print(f"[DEBUG] File path: {file_path}")

        os.makedirs(Config.GENERATED_CODE_PATH, exist_ok = True)
        
        with open(file_path, "w") as f:
            clean_code = code.strip("`").replace("python", "", 1).strip()
            f.write(clean_code)

        # Store the generated code in lifelong memory
        self.memory.add_memory(
            clean_code,
            metadata={"task": task.get("description"), "file": file_name},
            salience=1.0,
        )
        #Commit to Git
        try:
            commit_generated_code(file_path, f"Add generated code for task: {task['description']}")
        except Exception as e:
            print(f"[WARN] Git commit failed: {str(e)}")
