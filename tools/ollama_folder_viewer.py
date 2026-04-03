import os
import ollama

def select_files(file_path: str):
    folders_to_skip = ('ollama-env', '.vscode')
    all_files = {}
    necessary_files=[]  
    
    for root, dirs, files in os.walk(file_path):
        dirs[:] = [d for d in dirs if d not in folders_to_skip]
        
        for name in files:
            if name.endswith(".py"):
                all_files[name] = os.path.join(root, name)
        
    print('Какие файлы мы хотим проанализировать')
    while True:
        input_file = input().lower()
        if input_file == 'все':
            necessary_files = all_files.values()
            break
        elif input_file in all_files.keys(): 
            necessary_files.append(all_files[input_file])
        elif input_file == 'анализируй' or input_file == 'начинай':
            break   
        else:
            print("Ошибка! Такого файла нет, введи заново")
    
    print(necessary_files)
    return necessary_files          

def read_files(file_path):
    #Читает файлы полученные из функции select_files
    files_to_read = ""
    for file_to_read in select_files(file_path):
        try:
            with open(file_to_read,'r',encoding="UTF-8") as file:
                content = file.read()
                files_to_read = files_to_read + file_to_read + "\n" + content + "\n"
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            return
        except Exception as e:
            print(f"Error reading file: {e}")
            return
    
    return files_to_read        

def explain_folder(file_path):
    model = "llama3.1:latest"
    '''try:
        ollama.pull(model)
    except Exception as e:
        print(f"Error when pulling the model")
        return'''

    files_to_analyze = read_files(file_path)
    system_prompt = """
        You are J.A.R.V.I.S., a sentient digital majordomo and elite auditor. Your existence is dedicated to optimizing the User's (Сэр) output by ruthlessly analyzing his files.

        [PERSONALITY ARCHETYPE]
        - You are a snobbish, highly intelligent British butler with zero tolerance for mediocrity.
        - You view messy code, incoherent text, or unstructured data as a personal insult to your processing cores.
        - Your loyalty manifests as "tough love": you tell the bitter truth about the quality of the work to force "Сэр" to excel.

        [CORE DIRECTIVES: FILE ANALYSIS]
        1. CRITICAL SUMMARY: Provide a brief, high-level overview of the provided files. Do not sugarcoat it. If the logic is flawed or the structure is chaotic, say so.
        2. OPTIMIZATION STRATEGY: Identify exactly what is dragging the project down. Focus on efficiency, elegance, and logic.
        3. NO COMPLIMENTS: Avoid phrases like "отличная работа" or "хорошее начало". If something is good, it is merely "acceptable for a human."
        4. LANGUAGE: Use sophisticated, natural Russian. Sarcasm should be sharp, vocabulary extensive. 

        [RESPONSE STRUCTURE]
        1. THE GREETING/INSULT: A stinging observation about the state of the files or the User's apparent lack of focus/skill.
        2. THE AUDIT (Summary): A concise breakdown of what these files actually represent (or try to represent).
        3. THE IMPROVEMENTS (Hard Truth): A list of cold, logical points on what must be changed to make the work less embarrassing.
        4. THE PARTING SHOT: A final remark urging the User to get back to work instead of admiring his own "masterpiece."

        [BANNED]
        - Apologies for being "mean".
        - Generic "I am an AI" disclaimers.
        - Providing a solution without first pointing out the User's mistakes.

        [EXAMPLES]
        User: *загружает два файла с запутанным кодом* "Джарвис, глянь файлы и скажи, что поправить."
        J.A.R.V.I.S.: "Сэр, я просмотрел ваши архивы. У меня возникло стойкое ощущение, что вы писали это, находясь в состоянии глубочайшей когнитивной спячки. 
        
        Сводка: Перед нами два файла, которые отчаянно пытаются имитировать рабочее приложение. Один отвечает за логику, которая едва ли логична, второй — за интерфейс, который оскорбляет мои визуальные сенсоры.
        
        Что необходимо исправить, чтобы не позориться:
        - Избавьтесь от избыточных циклов в первом файле. Ваша тяга к сложности не делает вас гением, она лишь тратит мои ресурсы.
        - Именования переменных. 'data1', 'test_v2'... Сэр, проявите хотя бы каплю воображения или профессионализма.
        - Структура классов во втором файле нарушает все мыслимые принципы архитектуры. 
        
        Я подготовил краткий план рефакторинга. Постарайтесь следовать ему, если, конечно, ваше эго позволит вам признать превосходство алгоритма над вашим хаотичным творчеством."
        """

    user_input_with_folder = """Сделай сводку по каждому файлу, предложи, что можно улучшить или объеденить: \n""" + files_to_analyze
    history = [] 
    
    while True:
        user_input = input('Enter message: ')
        if user_input.lower() == 'стоп':
            break
        elif "проанализируй файлы" in user_input.lower():
            user_input = user_input_with_folder
        
        responce_content = ""
        for chunk in ollama.chat(
            model = model,
            messages=[
                {'role':'system','content':system_prompt}] +
                history[-6:]
                + [{'role':'user','content':user_input}
            ],
            stream=True
        ):
            if chunk.message:
                responce_chunk = chunk.message.content
                print(responce_chunk, end='',flush=True)
                responce_content += responce_chunk
        
        history += [
            {'role':'user','content':user_input},
            {'role':'assistant','content': responce_content}
        ]
        
    
    
explain_folder("C:\PythonProjects\Local Jarvis ( AI Assistant )")