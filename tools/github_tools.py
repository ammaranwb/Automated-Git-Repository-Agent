
from langchain_core.tools import tool

from services.github_client import get_github_client, get_github_repo


@tool
def list_github_repositories(limit: int = 10) -> str:
    """List repositories accessible to the authenticated GitHub user."""

    client = get_github_client()

    try:
        repositories = client.get_user().get_repos()

        results = []

        for repo in repositories[:min(limit, 30)]:
            results.append({
                "name": repo.full_name,
                "private": repo.private,
                "default_branch": repo.default_branch,
                "url": repo.html_url
            })

        return str(results)

    finally:
        client.close()


@tool
def get_repository_info(repo_name: str = "") -> str:
    """Get remote repository information including branches and URL."""

    client, repo = get_github_repo(repo_name or None)

    try:
        branches = [
            branch.name
            for branch in repo.get_branches()
        ]

        return str({
            "name": repo.full_name,
            "description": repo.description,
            "default_branch": repo.default_branch,
            "branches": branches,
            "url": repo.html_url,
            "stars": repo.stargazers_count,
            "open_issues": repo.open_issues_count
        })

    finally:
        client.close()


@tool
def list_github_issues(
    repo_name: str = "",
    state: str = "open",
    limit: int = 10
) -> str:
    """List GitHub issues. State can be open, closed or all."""

    if state not in ["open", "closed", "all"]:
        return "Invalid state. Use open, closed or all."

    client, repo = get_github_repo(repo_name or None)

    try:
        issues = repo.get_issues(state=state)

        results = []

        for issue in issues:
            if issue.pull_request:
                continue

            results.append({
                "number": issue.number,
                "title": issue.title,
                "state": issue.state,
                "url": issue.html_url,
                "labels": [
                    label.name for label in issue.labels
                ]
            })

            if len(results) >= min(limit, 30):
                break

        return str(results)

    finally:
        client.close()


@tool
def list_github_pull_requests(
    repo_name: str = "",
    state: str = "open",
    limit: int = 10
) -> str:
    """List pull requests in a GitHub repository."""

    if state not in ["open", "closed", "all"]:
        return "Invalid state. Use open, closed or all."

    client, repo = get_github_repo(repo_name or None)

    try:
        pull_requests = repo.get_pulls(
            state=state,
            sort="created",
            direction="desc"
        )

        results = []

        for pr in pull_requests:
            results.append({
                "number": pr.number,
                "title": pr.title,
                "state": pr.state,
                "author": pr.user.login if pr.user else None,
                "head": pr.head.ref,
                "base": pr.base.ref,
                "url": pr.html_url
            })

            if len(results) >= min(limit, 30):
                break

        return str(results)

    finally:
        client.close()


github_tools = [
    list_github_repositories,
    get_repository_info,
    list_github_issues,
    list_github_pull_requests
]