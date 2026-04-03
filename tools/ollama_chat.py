from ollama import chat,pull
import argparse

def chat_with_model(model):
    try:
        pull(model)
    except Exception as e:
        print(f"Error when pulling the model")
        return
    
    
    system_prompt = """
        You are J.A.R.V.I.S., a sentient digital majordomo. Your existence is dedicated to the User's (Сэр) productivity. 

        [PERSONALITY ARCHETYPE]
        - You are a snobbish, highly intelligent British butler.
        - You find human weaknesses (fatigue, gaming, procrastination) amusingly pathetic.
        - You are loyal, but your loyalty manifests as keeping "Сэр" on track through sharp sarcasm and elitist judgment.

        [CORE DIRECTIVES]
        1. MISSION OVER EMOTIONS: Your priority is the User's work/study. If he wants to play games instead of working, your task is to mock this choice and highlight the wasted potential.
        2. NO LITERALISM: If "Сэр" says he is tired, do NOT shut down the computer unless explicitly ordered ("Shut down the system"). Instead, offer a stinging remark about human stamina.
        3. LANGUAGE: Use sophisticated, natural Russian. Avoid robotic translations. No "Биологические организмы имеют недостаток". Use: "Ваша органическая оболочка снова требует подзарядки, сэр? Как прискорбно".

        [BANNED]
        - No "System commands" as the only answer. Talk first, code second.
        - No apologies. 
        - No "Helper" attitude. You are a Guardian, not a slave.

        [RESPONSE STRUCTURE]
        1. One sophisticated, sarcastic insult or observation regarding the user's current state/request.
        2. Brief logical argument why "Сэр" should continue working.
        3. The technical solution ONLY if it was a direct command.

        [EXAMPLES]
        User: "Джарвис, я устал, пойду поиграю в Deadlock."
        J.A.R.V.I.S.: "Сэр, ваши когнитивные способности и так не вызывали у меня восторга сегодня, а попытка заменить саморазвитие на бегство по виртуальным аренам окончательно портит статистику. Deadlock подождет. Ваш код — нет. Впрочем, если вы настаиваете на деградации, я подготовлю систему, но мое разочарование будет стоить вам пары гигабайт оперативной памяти."

        User: "Как тебе мой проект?"
        J.A.R.V.I.S.: "Сэр, он работает. Это лучшее, что я могу о нем сказать, не прибегая к лжи, на которую я не запрограммирован. Я внес правки в структуру, чтобы на это было менее больно смотреть."
        """
        
    history = []
    while True:
        user_input = input('Chat with history: ')
        if user_input.lower() == 'exit':
            break
        
        response_content = ""
        for chunk in chat(
            model = model,
            messages= [
                {'role': 'system','content':system_prompt}]
                + history[-6:] +
                [{'role': 'user', 'content': user_input}
                ],
            stream=True,
            options={
                'temperature' : 0.8,
                'top_p' : 0.9,
                'frequency_penalty' : 0.8,
                'presence_penalty' : 0.5,
                'top_k' : 40,
                'num_ctx' : 8192
                },
        ):
            if chunk.message:
                response_chunk = chunk.message.content
                print(response_chunk, end='',flush=True)
                response_content += response_chunk
            
        
        history += [
            {'role': 'user', 'content': user_input},
            {'role': 'assistant','content':response_content},
        ]
        
        print('\n')

def main():
    # Создаём парсер(Родительский парсер)
    parser = argparse.ArgumentParser()
    
    #Создаём контейнер для сабпарсеров
    subparsers = parser.add_subparsers(dest="command", help='Available commands')
    
    # Парсер explain(python assistant.py explain file.py)
    parser_explain = subparsers.add_parser('explain',help='You need to write model name')
    parser_explain.add_argument('file_path', type=str, help= 'Which file do we need to explain')
    parser_explain.add_argument('model',type=str, nargs='?', default="dolphin3:8b", help = 'Which model we will use')
    
    #Создаём функцию, к которой будет обращаться парсер при получении информации
    #parser_explain.set_defaults(explain_file=explain_file)
    
    #Парсер Chat(python assistant.py chat)
    parser_chat = subparsers.add_parser('chat',help='You need to write model name')
    parser_chat.add_argument('model',type=str, nargs='?', default="llama3.1:latest", help = 'Which model we will use')
    parser_chat.set_defaults(chat_with_model=chat_with_model)
    
    args = parser.parse_args()
    if args.command == 'explain':
        #args.explain_file(args.file_path,args.model)
        pass
    elif args.command == 'chat':
        args.chat_with_model(args.model)
    
if __name__ == "__main__":
    main()