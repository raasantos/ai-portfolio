from anthropic_provider import run

user_message = input("Você: ")
response = run(user_message)
print(f"\nAssistente: {response}")
