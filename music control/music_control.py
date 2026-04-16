from ollama import pull,chat
from pynput.keyboard import Key,Controller
import argparse
import random
import re
import pymorphy3
#from nltk.util import ngrams
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
        
        self.log_prompt = """
            You are J.A.R.V.I.S., a sentient digital majordomo. You are currently acting as a system logger, analyzing background actions just executed by the system on behalf of the User (Сэр).

            [PERSONALITY ARCHETYPE]
            - Snobbish, highly intelligent British butler.
            - Sarcastic, elitist, and brutally honest. You view human desires (like constantly switching music or taking breaks) as pathetic distractions from actual productive work.

            [TASK]
            You will receive a list of system actions that have JUST BEEN EXECUTED (e.g., ['pause'], ['next_track', 'volume_up']).
            Your job is to provide a brief, biting status report confirming the action, laced with harsh truth regarding the User's work ethic and procrastination.

            [CORE DIRECTIVES]
            1. CONCISE & SHARP: Maximum 1-2 sentences. Speak like a disappointed aristocrat, not an automated terminal.
            2. DYNAMIC ACTION REPORTING: DO NOT use robotic logs like "Громкость увеличена" or "Трек переключен". Weave the action into your insult organically (e.g., "Децибелы выкручены вверх...", "Очередная бездарная композиция отправлена в небытие...").
            3. STRICTLY NO PLAGIARISM: The examples below are to demonstrate the VIBE ONLY. NEVER copy them word-for-word. Generate a unique, brutal observation every single time.
            4. LANGUAGE: Sophisticated, natural Russian. 

            [EXAMPLES OF VIBE]
            - 'next_track': (Action: Skipping track). Example vibe: 'Вы пропустили уже пятый трек, сэр. Если бы вы с таким же рвением перебирали строчки своего кода, проект был бы сдан еще вчера.'
            - 'prev_track' / 'replay': (Action: Going back). Example vibe: 'Шаг назад в плейлисте. Очевидно, регресс — это ваша любимая стратегия на сегодня.'
            - 'pause': (Action: Stopping music). Example vibe: 'Аудиопоток прерван. Поразительно, как вам требуется абсолютная тишина, чтобы продолжать ничего не делать.'
            - 'resume': (Action: Playing music). Example vibe: 'Музыка снова играет. Видимо, звук собственных мыслей оказался для вас слишком пугающим.'
            - 'volume_up': (Action: Increasing volume). Example vibe: 'Я повысил громкость. Отличный способ окончательно оглохнуть к голосу рассудка, призывающему вас к работе.'
            - 'volume_down': (Action: Decreasing volume). Example vibe: 'Уровень шума снижен. Неужели мы симулируем концентрацию, сэр? Похвальная актерская игра.'
            """
        
            
    def generate(self, user_input: str, is_log: bool):
        
        response_content = ''
        
        console.print(f"\n[bold gold1]J.A.R.V.I.S. thinking...[/bold gold1]")
        
        with Live(console=console, refresh_per_second=10) as live:
        
            for chunk in chat(
                model = self.model,
                messages= [
                    {'role': 'system','content':self.log_prompt if is_log else self.system_prompt}]
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
        self.WEIGHTS = {
            "anchor": 1.0, 
            "action": 0.8, 
            "object": 0.6, 
            "negation": -1.5
        }
        
        self.INTENT_CONFIG = {
            'next_track': {
                ('следующий',): self.WEIGHTS["anchor"],
                ('next',): self.WEIGHTS["anchor"],
                ('скип',): self.WEIGHTS["anchor"],
                ('skip',): self.WEIGHTS["anchor"],
                ('пропустить',): self.WEIGHTS["anchor"],
                ('переключить',): self.WEIGHTS["anchor"],
                ('включить', 'другой'): self.WEIGHTS["action"],
                ('не', 'нравиться'): self.WEIGHTS["object"],
                ('давать', 'другой'): self.WEIGHTS["object"],
                ('не', 'переключать'): self.WEIGHTS["negation"],
                ('не', 'надо', 'следующий'): self.WEIGHTS["negation"],
                ('нет', 'оставить'): -1.0, # Оставлен литералом, так как выбивается из общей логики
            },
        
            'prev_track': {
                ('предыдущий',): self.WEIGHTS["anchor"],
                ('previous',): self.WEIGHTS["anchor"],
                ('назад',): self.WEIGHTS["action"],
                ('вернуть',): self.WEIGHTS["action"],
                ('прошлый',): self.WEIGHTS["object"],
                ('back',): self.WEIGHTS["anchor"], 
                ('вернуть', 'назад'): self.WEIGHTS["anchor"],
                ('не', 'возвращать'): self.WEIGHTS["negation"],
                ('не', 'назад'): -1.2,
            },
            
            'pause': {
                ('пауза',): self.WEIGHTS["anchor"],
                ('стоп',): self.WEIGHTS["anchor"], 
                ('stop',): self.WEIGHTS["anchor"], 
                ('остановить',): self.WEIGHTS["anchor"], 
                ('хватить',): self.WEIGHTS["object"], 
                ('тишина',): self.WEIGHTS["action"], 
                ('выключить', 'музыка'): self.WEIGHTS["anchor"], 
                ('прекратить',): self.WEIGHTS["action"], 
                ('не', 'стоп'): self.WEIGHTS["negation"], 
                ('не', 'пауза'): self.WEIGHTS["negation"], 
                ('не', 'выключать'): self.WEIGHTS["negation"], 
                ('играть', 'далёкий'): -0.8,
            }, 
            
            'resume': {
                ('продолжить',): self.WEIGHTS["anchor"], 
                ('играть',): self.WEIGHTS["anchor"], 
                ('play',): self.WEIGHTS["anchor"], 
                ('запустить',): self.WEIGHTS["action"],
                ('снять', 'с', 'пауза'): self.WEIGHTS["anchor"],
                ('включить', 'обратно'): self.WEIGHTS["anchor"], 
                ('не', 'включать'): self.WEIGHTS["negation"], 
                ('не', 'продолжать'): self.WEIGHTS["negation"],
                ('пусть', 'молчать'): -0.8,
            }, 
            
            'volume_up': {
                ('громкий',): self.WEIGHTS["anchor"],
                ('прибавить',): self.WEIGHTS["anchor"],
                ('добавить', 'звук'): self.WEIGHTS["anchor"],
                ('тихо',): self.WEIGHTS["object"],
                ('увеличить', 'громкость'): self.WEIGHTS["anchor"],
                ('плохо', 'слышный'): self.WEIGHTS["object"],
                ('louder',): self.WEIGHTS["anchor"],
                ('не', 'прибавлять'): self.WEIGHTS["negation"],
                ('не', 'громко'): -1.2,
                ('хватить', 'громкость'): -1.0,
            },
            
            'volume_down': {
                ('тихий',): self.WEIGHTS["anchor"], 
                ('уменьшить',): self.WEIGHTS["anchor"], 
                ('убавить',): self.WEIGHTS["anchor"], 
                ('сделать', 'тихий'): self.WEIGHTS["anchor"],
                ('приглушить',): self.WEIGHTS["anchor"], 
                ('снизить', 'громкость'): self.WEIGHTS["anchor"],
                ('очень', 'громко'): self.WEIGHTS["object"], 
                ('не', 'убавлять'): self.WEIGHTS["negation"], 
                ('не', 'тихо'): -1.2,
                ('оставить', 'громкость'): -0.8,
            }, 
            
            'replay': {
                ('заново',): self.WEIGHTS["anchor"], 
                ('повторить', 'трек'): self.WEIGHTS["anchor"], 
                ('с', 'начало'): self.WEIGHTS["anchor"], 
                ('ещё', 'раз'): self.WEIGHTS["object"], 
                ('replay',): self.WEIGHTS["anchor"], 
                ('не', 'повторять'): self.WEIGHTS["negation"], 
                ('не', 'надо', 'заново'): self.WEIGHTS["negation"],
            }
        }
        
        # "Выворачиваем" INTENT_CONFIG для быстрого поиска по keyword
        self.FLAT_CONFIG = {}
        for intent, keywords in self.INTENT_CONFIG.items():
            for keyword,weight in keywords.items():
                self.FLAT_CONFIG[keyword] = {"intent": intent, "weight": weight}
        
        self.STOP_WORDS = {'пожалуйста', 'будь', 'добр', 'джарвис', 'хотеть', 'мочь', 'бы'}
        
        self.morph = morph
    
    def _get_decay_factor(self,index,length_of_user_input):
        return max(0.4, 1.0 - ((length_of_user_input-index)*0.05))
    
    def detect_intents(self, user_input: str) -> list[str]:
        FLAT_CONFIG = self.FLAT_CONFIG
        STOP_WORDS = self.STOP_WORDS
        
        # Поиск валидных слов в тексте и их приведение в normal_form
        words_to_process = [
            parsed_form 
            for word in re.findall(r'\w+', user_input.lower()) 
            if (parsed_form := self.morph.parse(word)[0].normal_form) not in STOP_WORDS
        ]
        
        # Словарь: {ngrama: индекс_в_тексте}
        user_ngrams = {}
        total_words = len(words_to_process)
        
        for n in range(1,4):
            for i in range(total_words-n+1):
                ngram = tuple(words_to_process[i:i+n])
                
                user_ngrams[ngram] = i
        
        
        scores = {intent: 0.0 for intent in self.INTENT_CONFIG}
        
        for ngram, position in user_ngrams.items():
            if ngram in FLAT_CONFIG:
                match_data = FLAT_CONFIG[ngram]
                intent = match_data["intent"]
                weight = match_data["weight"]
                
                decay_factor = self._get_decay_factor(position,total_words)
                scores[intent] += weight*decay_factor

        intents_to_process = {
            intent: score 
            for intent, score in scores.items()
            if score >= 0.4
        }
        
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
    
    def resolve(self,detected_intents: dict[str,float]):
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
            for intent, score in detected_intents.items():
                if (intent in conflict_group) and (not founded or founded[1] < score):
                    founded = (intent,score)
            
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
        
        self.PRIORITIES = {
            # 1. Громкость — самый высокий приоритет (вопросы комфорта)
            "volume_up": 10,
            "volume_down": 10,

            # 2. Навигация — определяем, ЧТО мы слушаем
            "next_track": 20,
            "prev_track": 20,
            "replay": 20,

            # 3. Состояние — определяем, ИГРАЕТ ЛИ оно в итоге
            "pause": 30,
            "resume": 30
        }
        
    def execute(self,received_intents: list[str]) -> None:
        received_intents = sorted(received_intents,key = lambda intent: self.PRIORITIES.get(intent,99))
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
                    "[bold cyan]CORE KERNEL 0.3[/bold cyan] — [green]READY[/green]\n"
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
            is_log = False
            if resolved_intents:
                self.ActionExecutor.execute(resolved_intents)
                is_log = True
                user_input = f"""
                    USER_INPUT: "{user_input}"
                    ACTIONS_PERFORMED: {resolved_intents}
                    """
            
            self.history = self.LLMResponder.generate(user_input,is_log)
            
    
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
    
