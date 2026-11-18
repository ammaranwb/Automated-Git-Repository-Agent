
import os

from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

REPO_PATH = os.path.realpath(
    os.getenv("REPO_PATH", "./test-repo")
)


@tool
def create_file(file_path: str, content: str = "") -> str:
    """Create a new file inside the configured Git repository."""

    full_path = os.path.realpath(
        os.path.join(REPO_PATH, file_path)
    )

    if os.path.commonpath(
        [REPO_PATH, full_path]
    ) != REPO_PATH:
        return "Error: Cannot create files outside the repository."

    if os.path.exists(full_path):
        return f"Error: {file_path} already exists."

    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    with open(full_path, "w", encoding="utf-8") as file:
        file.write(content)

    return f"Successfully created: {file_path}"
