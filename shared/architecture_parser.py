import re

def parse_architecture_plan(plan_path):
    print(f"[ArchitectureParser] Parsing architecture plan from: {plan_path}")
    
    with open(plan_path, "r") as f:
        plan_text = f.read()

    modules_section = re.search(r"## Modules and Files(.*?)##", plan_text, re.DOTALL)
    if not modules_section:
        print(f"[ArchitectureParser] Warning: No modules section found in {plan_path}")
        return []
    
    modules_text = modules_section.group(1).strip()
    module_lines = [line.strip() for line in modules_text.splitlines() if line.startswith("-")]

    tasks = []

    for line in module_lines:
        match = re.match(r"- ([\w_]+\.py): (.+)", line)
        if match:
            module_file = match.group(1)
            module_desc = match.group(2)

            task = {
                "agent": "Coding Agent",
                "description": f"Implement {module_file} module: {module_desc}",
                "output_file": module_file,
                "completed": False
            }

            test_task = {
                "agent": "Testing Agent",
                "description": f"Write tests for {module_file} module",
                "output_file": f"test_{module_file}",
                "input_file": module_file,
                "completed": False
            }

            print(f"[ArchitectureParser] Parsed task: {task}")
            tasks.append(task)
            tasks.append(test_task)
        
    return tasks