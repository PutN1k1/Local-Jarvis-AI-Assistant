from ollama import pull,chat
from pynput.keyboard import Key,Controller
import argparse
import random
import re
import pymorphy3
from nltk.util import ngrams
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.text import Text

console = Console()

class Music():
    def __init__(self):
        self.keyBoard = Controller()
         
    def next(self):
        self.keyBoard.press(Key.media_next)
        self.keyBoard.release(Key.media_next)
    
    # Если трек только начался, то нужен только один media_previous, нужно как-нибудь это отслеживать
    def prev(self):
        # Двойное нажатие для перехода именно на прошлый трек
        for _ in range(2):
            self.keyBoard.press(Key.media_previous)
            self.keyBoard.release(Key.media_previous)
        
    def replay(self):
        self.keyBoard.press(Key.media_previous)
        self.keyBoard.release(Key.media_previous)

    def toggle_playback(self):
        self.keyBoard.press(Key.media_play_pause)
        self.keyBoard.release(Key.media_play_pause)
        
    def inc_volume(self):
        self.keyBoard.press(Key.media_volume_up)
        self.keyBoard.release(Key.media_volume_up)
        
    def dec_volume(self):
        self.keyBoard.press(Key.media_volume_down)
        self.keyBoard.release(Key.media_volume_down)
                   
class LLMResponder():    
    def __init__(self,model: str, history: list[str]):
        self.model = model 
        
        self.history = history
        
        self.system_prompt = """
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
            
    def generate(self, user_input: str):
        
        response_content = ""
        
        console.print(f"\n[bold gold1]J.A.R.V.I.S. thinking...[/bold gold1]")
        
        with Live(console=console, refresh_per_second=10) as live:
        
            for chunk in chat(
                model = self.model,
                messages= [
                    {'role': 'system','content':self.system_prompt}]
                    + self.history[-6:] +
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
                    response_content += response_chunk
                    live.update(Panel(Markdown(response_content), title="[bold white]Response[/bold white]", border_style="gold1"))
                
            self.history += [
                {'role': 'user', 'content': user_input},
                {'role': 'assistant','content':response_content},
            ]
                
        print('\n')
        
        return self.history

class IntentDetector():
    def __init__(self, morph: pymorphy3.MorphAnalyzer):
        self.INTENT_CONFIG = {
            'next_track': {
                ('следующий',): 1.0,
                ('next',): 1.0,
                ('скип',): 1.0,
                ('skip',): 1.0,
                ('пропустить',): 0.9,
                ('переключить',): 0.9,
                ('включить', 'другой'): 0.8,
                ('не', 'нравиться'): 0.5,
                ('давать', 'другой'): 0.6,
                ('не', 'переключать'): -1.5,
                ('не', 'надо', 'следующий'): -1.5,
                ('нет', 'оставить'): -1.0
            },
        
            'prev_track': {
                ('предыдущий',): 1.0,
                ('previous',): 1.0,
                ('назад',): 0.8,
                ('вернуть',): 0.8,
                ('прошлый',): 0.7,
                ('back',): 0.9, 
                ('вернуть', 'назад'): 1.0,
                ('не', 'возвращать'): -1.5,
                ('не', 'назад'): -1.2
            },
            
            'pause': {
                ('пауза',): 1.0,
                ('стоп',): 1.0, 
                ('stop',): 1.0, 
                ('остановить',): 0.9, 
                ('хватить',): 0.7, 
                ('тишина',): 0.8, 
                ('выключить', 'музыка'): 0.9, 
                ('прекратить',): 0.8, 
                ('не', 'стоп'): -1.5, 
                ('не', 'пауза'): -1.5, 
                ('не', 'выключать'): -1.5, 
                ('играть', 'далёкий'): -0.8
            }, 
            
            'resume': {
                ('продолжить',): 1.0, 
                ('играть',): 0.9, 
                ('play',): 1.0, 
                ('запустить',): 0.8,
                ('снять', 'с', 'пауза'): 1.0,
                ('включить', 'обратно'): 0.9, 
                ('не', 'включать'): -1.5, 
                ('не', 'продолжать'): -1.5,
                ('пусть', 'молчать'): -0.8    
            }, 
            
            'volume_up': {
                ('громкий',): 1.0,
                ('прибавить',): 0.9,
                ('добавить', 'звук'): 0.9,
                ('тихо',): 0.6,
                ('увеличить', 'громкость'): 1.0,
                ('плохо', 'слышный'): 0.7,
                ('louder',): 1.0,
                ('не', 'прибавлять'): -1.5,
                ('не', 'громко'): -1.2,
                ('хватить', 'громкость'): -1.0
            },
            
            'volume_down': {
                ('тихий',): 1.0, 
                ('убавить',): 0.9, 
                ('сделать', 'тихий'): 1.0,
                ('приглушить',): 0.9, 
                ('снизить', 'громкость'): 1.0,
                ('очень', 'громко'): 0.7, 
                ('не', 'убавлять'): -1.5, 
                ('не', 'тихо'): -1.2,
                ('оставить', 'громкость'): -0.8
            }, 
            
            'replay': {
                ('заново',): 1.0, 
                ('повторить', 'трек'): 1.0, 
                ('с', 'начало'): 0.9, 
                ('ещё', 'раз'): 0.7, 
                ('replay',): 1.0, 
                ('не', 'повторять'): -1.5, 
                ('не', 'надо', 'заново'): -1.5
            }
        }
        
        # За что отвечает каждый индекс
        # 0 - сумма point
        # 1 - кол-во повторений, потом делим, чтобы найти среднее значение
        # 2 - позиция в тексте
        self.SCORES = {
            "next_track" : [0.0,0.0,0.0],
            "prev_track" : [0.0,0.0,0.0],
            "pause" : [0.0,0.0,0.0],
            "resume" : [0.0,0.0,0.0],
            "volume_up" : [0.0,0.0,0.0],
            "volume_down" : [0.0,0.0,0.0],
            "replay" : [0.0,0.0,0.0],
        }
        
        self.morph = morph
        
    def detect_intents(self, user_input: str) -> list[str]:
        INTENT_CONFIG = self.INTENT_CONFIG
        SCORES = self.SCORES
        
        # Поиск отдельных слов в тексте и их приведение в normal_form
        words_to_process = [self.morph.parse(word)[0].normal_form for word in re.findall(r'\w+', user_input.lower())]
        ngrams_of_words = ()
        priority = 0
        
        #Создаём ngrams(пары) слов, чтобы потом искать их в INTENT_CONFIG
        for i in range(1,4):
            ngrams_of_words += tuple(ngrams(words_to_process,i))
        
        for intent, keywords in INTENT_CONFIG.items():
            for keyword,score in keywords.items():
                if keyword in ngrams_of_words:
                    SCORES[intent][0] += score
                    SCORES[intent][1] += 1.0
                    SCORES[intent][2] = priority
                    priority += 1
        
        intents_to_process = {keyword : score[2] for keyword,score in self.SCORES.items() if (score[0] > 0.0) and (score[0]/score[1]) >= 0.7}
        
        for keyword,score in self.SCORES.items():
            SCORES[keyword] = [0.0,0.0,0.0]
        
        return intents_to_process

class IntentResolver():
    def __init__(self):
        
        self.CONFLICT_GROUPS = (
            # Группа 1: Состояние плеера (Вкл/Выкл)
            ('pause', 'resume'),
            
            # Группа 2: Вектор громкости (Тише/Громче)
            ('volume_up', 'volume_down'),
            
            # Группа 3: Навигация (Куда мотаем)
            # Replay здесь тоже, так как это команда изменения текущего индекса трека
            ('next_track', 'prev_track', 'replay')
        )
    
    def resolve(self,detected_intents):
        verified_intents = []
        
        # Если intent ни в одном конфликте не участвует, то он валиден
        for intent in list(detected_intents.keys()): 
            if any(intent in conflict_group for conflict_group in self.CONFLICT_GROUPS):
                continue
            else:
                verified_intents.append(intent)
                del detected_intents[intent]
        
        # Проверка intents по каждой группе конфликтов
        for conflict_group in self.CONFLICT_GROUPS:
            founded = ()
            # Нужно оптимизировать поиск, чтобы каждый раз не смотреть обработанные intents
            for intent, position in detected_intents.items():
                if (intent in conflict_group) and (not founded or founded[1] < position):
                    founded = (intent,position)
            
            if founded:
                verified_intents.append(founded[0])
        
        return verified_intents
        
                
class ActionExecutor():
    def __init__(self, music : Music):
        self.music = music
        
        self.INTENT_ACTIONS = {
            "next_track": self.music.next,
            "prev_track": self.music.prev,
            "pause": self.music.toggle_playback,
            "resume": self.music.toggle_playback,
            "replay": self.music.replay,
            "volume_up": self.music.inc_volume,
            "volume_down": self.music.dec_volume
        }
        
    def execute(self,received_intents: list[str]) -> None:
        for intent in received_intents:
            action = self.INTENT_ACTIONS.get(intent)
            if action: 
                action()

class JarvisCore(): # Jarvis Agent, specializes in music
    def __init__(self, model: str, music: Music, morph: pymorphy3.MorphAnalyzer):  
        self.music = music
        
        self.history = []
        
        self.LLMResponder = LLMResponder(model,self.history)
        self.IntentDetector = IntentDetector(morph)
        self.IntentResolver = IntentResolver()
        self.ActionExecutor = ActionExecutor(music)
        
    def handle_input(self):
        
        console.print(
                Panel.fit(
                    "[bold white]PERSONAL AI ASSISTANT[/bold white]\n"
                    "[bold cyan]CORE KERNEL 0.2[/bold cyan] — [green]READY[/green]\n"
                    "[dim]Waiting for your command, Sir...[/dim]", 
                    subtitle="[bold gold1]J.A.R.V.I.S.[/bold gold1]",
                    border_style="cyan"
                )
            )        
        while True:
            user_input = Prompt.ask("[bold cyan]>>>[/bold cyan]")
            if user_input.lower() in ['exit', 'quit', 'выход']:
                console.print("[bold red]Система деактивирована.[/bold red]")
                break
            
            detected_intents = self.IntentDetector.detect_intents(user_input)
            resolved_intents = self.IntentResolver.resolve(detected_intents)
            if detected_intents:
                self.ActionExecutor.execute(detected_intents)
                user_input = f"""
                USER_INPUT: "{user_input}"
                ACTIONS_PERFORMED: {resolved_intents}
                """
            
            self.history = self.LLMResponder.generate(user_input)
            
    
def main():
    model = "dolphin3:8b"
    try:
        pull(model)
        print("J.A.R.V.I.S. ready to work")
    except Exception as e:
        print(f"Error when pulling the model")
        return
        
    
    music = Music()
    morph = pymorphy3.MorphAnalyzer()
    jarvis = JarvisCore(model = model, music = music, morph = morph)
    parser = argparse.ArgumentParser()
    jarvis.handle_input()
    subparsers = parser.add_subparsers(dest="command", help='Available commands')
    
    music_next_parser = subparsers.add_parser("next", help="plays next track")
    music_next_parser.set_defaults(music_next=music.next)
    
    music_prev_parser = subparsers.add_parser("prev", help="plays next track")
    music_prev_parser.set_defaults(music_prev=music.prev)
    
    parser_chat = subparsers.add_parser('chat',help='You need to write model name')
    parser_chat.set_defaults(chat_with_model=jarvis.handle_input)
    
    args = parser.parse_args()
    if args.command == 'next':
        args.music_next()
    elif args.command == 'prev':
        args.music_prev()
    elif args.command == 'chat':
        args.chat_with_model()
        
if __name__ == "__main__":
    main()
    
