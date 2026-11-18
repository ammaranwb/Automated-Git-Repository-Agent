
import os
import git

from dotenv import load_dotenv
from langchain_core.tools import tool
from contextlib import contextmanager

load_dotenv()

REPO_PATH = os.path.abspath(
    os.getenv("REPO_PATH", "./test-repo")
)


@contextmanager
def get_repo():
    repo = git.Repo(REPO_PATH)

    try:
        if repo.bare:
            raise ValueError("Repository is bare.")

        if not repo.head.is_valid():
            raise ValueError(
                "Repository has no initial commit."
            )

        yield repo

    finally:
        repo.close()



@tool
def get_git_status() -> str:
    """Get the current branch and working tree status."""

    with get_repo() as repo:
        return (
            f"Branch: {repo.active_branch.name}\n"
            f"Changes:\n{repo.git.status('--short')}"
        )


@tool
def create_branch(branch_name: str) -> str:
    """Create and switch to a new Git branch."""

    with get_repo() as repo:
        if branch_name in [b.name for b in repo.branches]:
            return f"Branch '{branch_name}' already exists."

        branch = repo.create_head(branch_name)
        branch.checkout()

        return f"Created and switched to branch: {branch_name}"


@tool
def stage_file(file_path: str) -> str:
    """Stage a specific file for the next commit."""

    with get_repo() as repo:
        repo_path = os.path.realpath(
            os.path.join(REPO_PATH, file_path)
        )

        if os.path.commonpath(
            [REPO_PATH, repo_path]
        ) != REPO_PATH:
            return "Error: File path is outside the repository."

        if not os.path.isfile(repo_path):
            return "Error: File does not exist."

        relative_path = os.path.relpath(
            repo_path, REPO_PATH
        )

        repo.index.add([relative_path])

        return f"Staged file: {relative_path}"


@tool
def commit_changes(message: str) -> str:
    """Commit staged changes with the given message."""

    with get_repo() as repo:
        if not repo.index.diff("HEAD") and not repo.untracked_files:
            return "No changes available to commit."

        repo.index.commit(message)

        return f"Successfully committed: {message}"


git_tools = [
    get_git_status,
    create_branch,
    stage_file,
    commit_changes
]