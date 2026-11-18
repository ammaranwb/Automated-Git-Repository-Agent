
import os

from dotenv import load_dotenv
from github import Auth, Github, GithubException

load_dotenv()


def get_github_client():
    """Create an authenticated GitHub client."""

    token = os.getenv("GITHUB_TOKEN")

    if not token:
        raise ValueError(
            "GITHUB_TOKEN is missing from .env"
        )

    auth = Auth.Token(token)

    return Github(auth=auth)


def get_github_repo(repo_name=None):
    """Return an authenticated GitHub repository."""

    client = get_github_client()

    repo_name = (
        repo_name
        or os.getenv("GITHUB_DEFAULT_REPO")
    )

    if not repo_name or "/" not in repo_name:
        client.close()
        raise ValueError(
            "Provide repository as owner/repository"
        )

    try:
        repo = client.get_repo(repo_name)
        return client, repo

    except GithubException:
        client.close()
        raise


def verify_github_connection():
    """Verify GitHub authentication."""

    client = get_github_client()

    try:
        user = client.get_user()

        return {
            "authenticated": True,
            "username": user.login,
            "name": user.name
        }

    finally:
        client.close()
