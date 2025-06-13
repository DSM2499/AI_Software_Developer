import git
from config.config import Config

def commit_generated_code(file_path, message):
    repo = git.Repo(".")
    repo.index.add([file_path])
    repo.index.commit(message)