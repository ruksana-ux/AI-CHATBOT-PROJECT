"""AI Customer Support Assistant - Terminal Chat Interface."""
from dotenv import load_dotenv
from assistant import CustomerSupportAssistant

load_dotenv()


def main():
    print("=" * 65)
    print("🤖 AI Customer Support Assistant (CLI Mode)")
    print("Type 'quit' or 'exit' to end the session.")
    print("=" * 65)
    print("\nAssistant: Hello! Welcome to Customer Support. How can I help you today?\n")

    assistant = CustomerSupportAssistant()
    history = []

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in {"quit", "exit", "bye"}:
            print("\nAssistant: Thank you for contacting customer support. Have a great day!")
            break

        response = assistant.process_message(user_input, history)
        print(f"\nAssistant: {response}\n")

        # Maintain session conversation history
        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
