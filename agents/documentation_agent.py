from openai import OpenAI
import os
from agents.base_agent import BaseAgent
from config.config import Config

class DocumentationAgent(BaseAgent):
    def run_task(self, task):
        print(f"[DocumentationAgent] run_task() called with task: {task}")

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
            You are a senior technical writer with extensive experience in documenting Python projects for open-source platforms like GitHub. 
            Your goal is to generate a high-quality `README.md` file that provides a clear, concise, and comprehensive overview of the project.

            **Given the following Python project source code, generate a high-quality `README.md` file.**

            **Code:**
            {code_content}

            **Instructions:**
            1.  **Analyze the Code:** Thoroughly analyze the provided `code_content` to understand its primary functionality, dependencies, and how it's intended to be used.
            2.  **Infer Purpose:** Based on your analysis, infer the project's purpose and its key features.
            3.  **Standard GitHub README Structure:** Adhere to common GitHub `README.md` best practices.
            4.  **Sections to Include:**
                * **Project Title:** A clear and concise title for the project.
                * **Description:** A brief overview of what the project does, its main features, and why it's useful. Aim for 2-3 paragraphs.
                * **Table of Contents (Optional but Recommended):** If the README becomes long, include a TOC for easy navigation.
                * **Usage Instructions:** Explain how to use the code. This might include:
                    * Command-line arguments.
                    * Function calls if it's a library.
                    * Any specific input requirements.
                    * Assumptions about the environment.
               * **Installation:** Provide clear, step-by-step instructions on how to set up the project. This should include:
                    * Prerequisites (e.g., Python version, `pip`).
                    * How to clone the repository.
                    * How to install dependencies (e.g., `pip install -r requirements.txt`).
                    * Any environment variable setup.
                * **Example Usage:** Provide one or more simple, executable code examples demonstrating how to use the project's core functionality. Include expected outputs if possible. Use clear code blocks.
                * **Contributing (Optional):** A brief section on how others can contribute to the project (e.g., "Contributions are welcome!").
            5.  **Markdown Formatting:** Use appropriate Markdown syntax for headings, code blocks, lists, and emphasis.
            6.  **Clarity and Conciseness:** Ensure the language is clear, concise, and easy for developers to understand. Avoid jargon where simpler terms suffice.
            7.  **No Explanations Outside README:** Generate only the `README.md` content. Do not include any additional commentary or explanations before or after the Markdown content.

            **Example Structure (adapt as needed):**

            ```markdown
            # Project Title

            ## Description
            [Brief description of the project]

            ## Table of Contents
            * [Link to Installation](#installation)
            * [Link to Usage Instructions](#usage-instructions)
            * [Link to Example Usage](#example-usage)
            * [Link to Contributing](#contributing)
            * [Link to License](#license)

            ## Installation
            [Step-by-step instructions]

            ## Usage Instructions
            [How to use the project]

            ## Example Usage
            ```python
            # [Code example]
    """
        try:
            #print(f"[DEBUG] Sending prompt to OpenAI...")
            client = OpenAI(api_key = Config.OPENAI_API_KEY)

            response = client.chat.completions.create(
                model = "gpt-3.5-turbo",
                messages = [{"role": "user", "content": prompt}],
                temperature = 0.2,
            )
            readme_content = response.choices[0].message.content
            #print(f"[DEBUG] Extracted README content: {readme_content}")
            self.log(f"Generated README content: {readme_content}")
        
        except Exception as e:
            print(f"[ERROR] Exception during OpenAI API call: {str(e)}")
            return
        
        #Save file
        readme_file_path = os.path.join(Config.README_PATH, f"{os.path.splitext(file_name)[0]}_README.md")
        with open(readme_file_path, "w") as f:
            f.write(readme_content)
        
        print(f"[DocumentationAgent] README file created: {readme_file_path}")