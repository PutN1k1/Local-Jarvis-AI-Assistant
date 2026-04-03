from ollama import generate

response = generate('llama3.1:latest', "can you read the files from folder")
print(response['response'])