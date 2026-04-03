from ollama import chat

history = []
while True:
    user_input = input('Chat with history: ')
    if user_input.lower() == 'exit':
        break
    
    responce_content = ""
    for chunk in chat(
        model = "llama3.1:latest",
        messages= history + [
            {'role': 'system','content':'You are a helpful assistant. You only give a short sentence by answer.'},
            {'role': 'user', 'content': user_input},
            ],
        stream=True
    ):
        if chunk.message:
            response_chunk = chunk.message.content
            print(response_chunk, end='',flush=True)
            responce_content += response_chunk
        
    
    history += [
        {'role': 'user', 'content': user_input},
        {'role': 'assistant','content':response_chunk},
    ]
    
    print('\n')