from ollama import chat,pull
import argparse

def explain_file(file_path,model):
    try:
        with open(file_path,'r') as file:
            content = file.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    try:
        pull(model)
    except Exception as e:
        print(f"Error when pulling the model")
    print(f"--- Analyzing {file_path} with {model}")
    
    # Получаем ответ модели
    try:
        response = chat(
            model=model,
            messages = [
                        {
                            "role": "system",
                            "content": """You are a senior Python engineer.
                                            Answer ONLY in Russian. Never switch language.
                                            Avoid repetition."""
                        },
                        {
                            "role": "user",
                            "content": f"""Explain this Python code step-by-step:

                                            1. What the script does
                                            2. Key functions
                                            3. Important logic
                                            4. Possible improvements

                                            Code:
                                            {content}"""
                    }
                ],
            stream=True
            )
    except Exception as e:
        print(f"Error communicating with Ollama: {e}")
        
    if response:
        print("Thinking...")
        for chunk in response:
            print(chunk.message.content, end='',flush=True)
            
def main():
    # Создаём парсер(Родительский парсер)
    parser = argparse.ArgumentParser()
    
    #Создаём контейнер для сабпарсеров
    subparsers = parser.add_subparsers(dest="command", help='Available commands')
    
    # Парсер данных(python assistant.py explain file.py)
    parser_explain = subparsers.add_parser('explain',help='You need to write model name')
    parser_explain.add_argument('file_path', type=str, help= 'Which file do we need to explain')
    parser_explain.add_argument('model',type=str, nargs='?', default="llama3.1:latest", help = 'Which model we will use')
    
    #Создаём функцию, к которой будет обращаться парсер при получении информации
    parser_explain.set_defaults(explain_file=explain_file)
    
    #Заготовка под generate
    parser_generate = subparsers.add_parser('generate',help='You need to write model name')
    parser_generate.add_argument('model',type=str, help = 'What model we will use')
    
    args = parser.parse_args()
    if args.command == 'explain':
        args.explain_file(args.file_path,args.model)
    
if __name__ == "__main__":
    main()