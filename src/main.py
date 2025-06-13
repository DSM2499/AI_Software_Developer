import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.coding_agent import CodingAgent
from shared.rag_utils import get_vector_store
from shared.queue import load_tasks, save_tasks
from agents.testing_agent import TestingAgent
from agents.qa_agent import QAAgent
from agents.documentation_agent import DocumentationAgent
from agents.refactor_agent import RefactorAgent
from agents.code_architect_agent import CodeArchitectAgent
from shared.task_manager import TaskManager
from shared.architecture_parser import parse_architecture_plan

task_manager = TaskManager()

agents = {
    "Coding Agent": CodingAgent(name = "Coding Agent", vector_store = get_vector_store()),
    "Refactoring Agent": RefactorAgent(name = "Refactoring Agent", vector_store = get_vector_store()),
    "Documentation Agent": DocumentationAgent(name = "Documentation Agent", vector_store = get_vector_store()),
    "Code Architect Agent": CodeArchitectAgent(name = "Code Architect Agent", vector_store = get_vector_store()),
    "Testing Agent": TestingAgent(name = "Testing Agent", vector_store = get_vector_store()),
    "QA Agent": QAAgent(name = "QA Agent", vector_store = get_vector_store()),
}

print("[Main] Starting Phase 6 loop...\n")

while True:
    task = task_manager.get_next_task()

    if task is None:
        print("[Main] No pending tasks remaining. Done.")
        break

    agent_name = task["agent"]
    agent = agents.get(agent_name)

    print(f"\n[Main] Processing task for agent: {agent_name} — Completed? {task.get('completed', False)}")

    if agent is None:
        print(f"[ERROR] Unknown agent: {agent_name}. Skipping task.")
        task_manager.mark_task_completed(task)  # Optional: mark unknown tasks to avoid loop
        continue

    try:
        if agent_name == "Code Architect Agent":
            architecture_plan_path = agent.run_task(task)
            if architecture_plan_path:
                task_manager.mark_task_completed(task)
                print("[Main] Parsing architecture plan...")
                new_tasks = parse_architecture_plan(str(architecture_plan_path[0]))
                for new_task in new_tasks:
                    task_manager.add_task(new_task)
        else:
            print(f">>> Calling {agent_name}.run_task()...")
            agent.run_task(task)
            print(f">>> run_task() completed.")
        
        if agent_name == "Coding Agent":
            print("[Main] Adding Refactoring and Documentation tasks...")
            output_file = task.get("output_file")
            description_base = task.get("description")

            #Refactoring task
            refactoring_task = {
                "agent": "Refactoring Agent",
                "description": f"Refactor and optimize code in {output_file} ({description_base})",
                "output_file": output_file + "_refactored.py",
                "input_file": output_file,
                "completed": False,
            }
            task_manager.add_task(refactoring_task)

            # Documentation task
            documentation_task = {
                "agent": "Documentation Agent",
                "description": f"Generate documentation for {output_file} ({description_base})",
                "output_file": output_file + "_docs.md",
                "input_file": output_file,
                "completed": False,
            }
            task_manager.add_task(documentation_task)

            task_manager.mark_task_completed(task)
        else:
            task_manager.mark_task_completed(task)

    except Exception as e:
        print(f"[ERROR] Exception while calling {agent_name} run_task(): {str(e)}")
        task_manager.mark_task_completed(task)

    time.sleep(1)
        
        