from ollama import generate

for chunk in generate('llama3.1:latest','How much time i need to spend to become senior ML developer',stream=True):
    print(chunk['response'], end='', flush=True)