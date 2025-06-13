# 📘 AI Software Engineering Agent Pipeline
Autonomous multi-agent system to architect, code, test, refactor, and document software — powered by LLMs
---

## 🗂 Project Overview
`ai_se_agent` is an AI-driven software engineering pipeline that automates software development tasks through a team of specialized AI agents.
It demonstrates how agentic workflows can autonomously:

✅ Architect a software package

✅ Implement production-quality code

✅ Generate tests for the code

✅ Refactor and optimize the code

✅ Generate documentation

✅ Do this iteratively, with clear task orchestration

It is designed to be a proof-of-concept for AI software engineering agents, with practical use cases in:
- Rapid prototyping
- Continuous integration pipelines
- Automated software scaffolding
- Agent-based development assistants

## 🏛️ Architecture

| Agent                | Role                                                       |
| -------------------- | ---------------------------------------------------------- |
| Code Architect Agent | Designs architecture, generates a module + class structure |
| Coding Agent         | Implements Python modules as per the architecture          |
| Testing Agent        | Generates comprehensive unit tests with pytest             |
| Refactoring Agent    | Refactors and optimizes existing code                      |
| Documentation Agent  | Generates high-quality Markdown documentation              |

### Pipeline Flow

Code Architect -> (Architecture Plan → parsed into tasks) ->
Coding Agent -> (Generated Code) ->
Testing Agent -> (Tests) ->
Refactoring Agent -> (Refactored code) ->
Documentation Agent -> (Markdown Docs)

## 🚀 Features
✅ Fully autonomous agent pipeline driven by OpenAI GPT models

✅ Modular agent architecture — easily extendable

✅ Architecture parser auto-generates coding tasks from Architect Agent outputs

✅ Streamlit UI for task submission + management

✅ Automatic task deduplication and persistence

✅ Modular task queue backed by tasks.json

✅ Supports local RAG (Retrieval-Augmented Generation) via LangChain + Chroma

✅ Git integration for tracking generated code

✅ Logging and traceability built in

## 🔍 Example Run (ETL Pipeline Example)

Resulting Pipeline:
- `csv_reader.py`
- `data_transformer.py`
- `db_loader.py`
- Corrosponding Tests:
  - `test_csv_reader.py`
  - `test_data_transformer.py`
  - `test_db_loader.py`
- Refactor versions:
  - `csv_reader.py_refactored.py`, etc.
- Documentation:
  - `csv_reader.py_docs.md`, etc.

## 🛠️ Installation

```bash
# Clone the repo
git clone https://github.com/yourusername/AI_Software_Developer.git
cd ai_se_agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

## 🏃 Running the Pipeline

### CLI Mode
```bash
python -m src.main
```

### Streamlit UI
```bash
streamlit run task_uploader.py
```
Use the UI to:
- ✅ Upload new tasks.json
- ✅ Add individual tasks via form
- ✅ Clear tasks
- ✅ Trigger pipeline run
