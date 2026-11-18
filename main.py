
from agent.git_agent import run_git_agent


def main():
    print("\n===== AI GIT ASSISTANT =====")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            break

        try:
            response = run_git_agent(user_input)
            print("\nGit Assistant:", response, "\n")

        except Exception as e:
            print(f"\nError: {e}\n")


if __name__ == "__main__":
    main()