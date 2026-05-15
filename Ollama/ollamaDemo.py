import ollama

# Changed model name to match your local 'ollama list' output
stream = ollama.chat(
    model='gemma:latest', 
    messages=[{'role': 'user', 'content': 'Write 5 metro state of india'}],
    stream=True,
)

for chunk in stream:
    print(chunk['message']['content'], end='', flush=True)
