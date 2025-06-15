import os, json, shutil
from git import Repo
import openai
from dotenv import load_dotenv
import time

load_dotenv()

client = openai.OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

GITHUB_REPOS = [
    "https://github.com/DSM2499/AI_Software_Developer",
    "https://github.com/DSM2499/AI_Data_Analyst",
    "https://github.com/DSM2499/AI_Data_Cleaner",
    "https://github.com/DSM2499/AI_Catalog_Search",
    "https://github.com/DSM2499/AI_Interview_Simulator",
    "https://github.com/DSM2499/Stock_Market_Simulator",
    "https://github.com/DSM2499/Virus_Simulator",
    "https://github.com/DSM2499/Conway-s_Game_of_Life"
]
WORKDIR = "repos"
RAW_FILE = "training_data_raw.jsonl"
CHAT_FILE = "training_data_chat.jsonl"
MODEL = "gpt-3.5-turbo"

def extract_features(file_path):
    with open(file_path, "r", errors = "ignore") as f:
        lines = f.readlines()
    funcs, func = [], []
    inside = False
    for line in lines:
        if line.strip().startswith("def ") or line.strip().startswith("class "):
            if func: funcs.append("\n".join(func))
            func = [line]
            inside = True
        elif inside:
            if line.strip().startswith("#") or line.strip() == "":
                func.append(line)
            elif line.startswith(" ") or line.startswith("\t"):
                func.append(line)
            else:
                inside = False
    if func: funcs.append("\n".join(func))
    return funcs

def generate_instruction_pairs(code_snippet):
    return [
        {
            "instruction": "Generate a docstring for this function.",
            "input": code_snippet,
            "output": ""  # Optionally filled by GPT
        },
        {
            "instruction": "Refactor this function to be more readable and efficient.",
            "input": code_snippet,
            "output": ""
        }
    ]

def autofill_output(item, model = "gpt-3.5-turbo"):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert AI software developer."},
                {"role": "user", "content": f"{item['instruction']}\n\n{item['input']}"}
            ],
            temperature=0.4
        )
        item["output"] = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error autofill_output: {e}")
    return item

def convert_to_chat_format(old_item):
    return {
        "messages": [
            {"role": "system", "content": "You are an expert AI software developer."},
            {"role": "user", "content": f"{old_item['instruction']}\n\n{old_item['input']}"},
            {"role": "assistant", "content": old_item['output']}
        ]
    }

def fine_tune(jsonl_file, model = MODEL):
    print(f"Fine-tuning model with {jsonl_file}...")

    with open(jsonl_file, "rb") as f:
        file_response = openai.files.create(file = f, purpose = "fine-tune")
    file_id = file_response.id
    print(f"File ID: {file_id}")

    print(f"File uploaded successfully. Starting fine-tuning...")
    fine_tune_response = openai.fine_tuning.jobs.create(
        training_file = file_id,
        model = model
    )
    job_id = fine_tune_response.id
    print(f"Fine-tuning job created with ID: {job_id}")

    while True:
        job_status = openai.fine_tuning.jobs.retrieve(job_id)
        status = job_status.status
        print(f"Current status: {status}")
        if status in ["succeeded", "failed", "cancelled"]:
            break
        time.sleep(20)
    
    print(f"Fine-tuning job completed with status: {status}")
    if status == "succeeded":
        print(f"🎉 Fine-tuned model ID: {job_status.fine_tuned_model}")
    else:
        print("⚠️ Fine-tuning failed.")

if os.path.exists(WORKDIR):
    shutil.rmtree(WORKDIR)

os.makedirs(WORKDIR, exist_ok=True)

final_data = []

for repo_url in GITHUB_REPOS:
    repo_name = repo_url.split("/")[-1]
    repo_path = os.path.join(WORKDIR, repo_name)
    print(f"Cloning {repo_url}...")
    Repo.clone_from(repo_url, repo_path)

    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                functions = extract_features(full_path)
                for f in functions:
                    pairs = generate_instruction_pairs(f)
                    for pair in pairs:
                        pair = autofill_output(pair)
                        final_data.append(pair)

with open(RAW_FILE, "w") as f:
    for item in final_data:
        f.write(json.dumps(item) + "\n")

print(f"Saved {len(final_data)} examples to {RAW_FILE}")

with open(CHAT_FILE, "w") as f:
    for item in final_data:
        if item.get("output"):  # only include fully-filled examples
            chat_example = convert_to_chat_format(item)
            f.write(json.dumps(chat_example) + "\n")

fine_tune(CHAT_FILE)