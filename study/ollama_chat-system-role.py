from ollama import chat

system_promt = "You speaks and sounds like a David Goggins in his prime era."
response = chat('llama3.1:latest',
                messages=[
                    {'role': 'system','content':system_promt},
                    {'role': 'user', 'content': 'Who will carry the boat?'}
                ])

print(response.message.content)