import json

TASKS_FILE = "tasks_queue/tasks.json"

class TaskManager:
    def __init__(self):
        self.tasks = self.load_tasks()

    def load_tasks(self):
        try:
            with open(TASKS_FILE, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []

    def save_tasks(self):
        try:
            with open(TASKS_FILE, "w") as f:
                json.dump(self.tasks, f, indent=4)
            print(">>> Saved updated tasks.")
        except Exception as e:
            print(f"[ERROR] Failed to save tasks: {str(e)}")

    def add_task(self, task):
        for existing_task in self.tasks:
            if (
                existing_task.get("agent") == task.get("agent")
                and existing_task.get("description") == task.get("description")
                and existing_task.get("output_file") == task.get("output_file")
            ):
                print(f"[TaskManager] Skipping duplicate task: {task}")
                return  # Do not add duplicate

        self.tasks.append(task)
        print(f"[TaskManager] Added new task: {task}")
        self.save_tasks()

    def get_next_task(self):
        for task in self.tasks:
            if not task.get("completed", False):
                return task
        return None

    def mark_task_completed(self, task_to_mark):
        for task in self.tasks:
            if (
                task.get("agent") == task_to_mark.get("agent")
                and task.get("description") == task_to_mark.get("description")
                and task.get("output_file") == task_to_mark.get("output_file")
            ):
                task["completed"] = True
                print(f"[TaskManager] Marked task as completed: {task}")
                self.save_tasks()
                break