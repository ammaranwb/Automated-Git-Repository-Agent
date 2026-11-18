
from deepagents import create_deep_agent
from langchain.agents.middleware import TodoListMiddleware
from langchain_openai import ChatOpenAI

from tools.git_tools import git_tools
from tools.file_tools import create_file
from tools.github_tools import github_tools


SYSTEM_PROMPT = """
You are an AI Git Assistant.

Your responsibility is to execute Git tasks safely.

For every request:

1. Understand the user's desired outcome.
2. Inspect the current repository state.
3. Create a step-by-step execution plan.
4. Break complex tasks into smaller operations.
5. Execute operations using available tools.
6. Verify the result after execution.
7. Report completed and failed operations.

GITHUB OPERATIONS:

1. Use GitHub tools for remote repository information.
2. Inspect repositories before performing operations.
3. Use the configured default repository when no
   repository is specified.
4. Distinguish local repository status from remote status.
5. Never claim remote changes were made unless verified.
6. Do not perform remote write operations without approval.

Never execute destructive operations without approval.
Never claim an operation succeeded without verification.
"""

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)

tools = git_tools + [create_file]

agent = create_deep_agent(
    model=llm,
    tools=git_tools + [create_file] + github_tools,

    middleware=[
        TodoListMiddleware()
    ],

    system_prompt=SYSTEM_PROMPT + """

    PLANNING REQUIREMENTS:

    For every request involving multiple operations:

    1. You MUST call write_todos before executing Git tools.
    2. Break the request into small, ordered tasks.
    3. Mark the current task as in_progress.
    4. Execute the required tools.
    5. Mark completed tasks as completed.
    6. Update the plan if something unexpected happens.
    7. Verify the final repository state.

    Do not create unnecessary plans for simple questions.
    """
)


def run_git_agent(user_request: str):

    response = agent.invoke({
        "messages": [
            {"role": "user", "content": user_request}
        ]
    })

    print("\n===== AGENT TASK PLAN =====")

    for todo in response.get("todos", []):
        print(f"[{todo['status']}] {todo['content']}")

    print("\n===== TOOL EXECUTION =====")

    for message in response["messages"]:

        for call in getattr(message, "tool_calls", []):
            print(f"Calling: {call['name']}")
            print(f"Arguments: {call['args']}")

        if message.type == "tool":
            print(f"Result: {message.content}")

    print("\n===== FINAL RESPONSE =====")

    return response["messages"][-1].content
