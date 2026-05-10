import ollama
import time

intents = ["next_track", "prev_track", "pause", "resume", "volume_up", "volume_down", "replay", "other"]

personas = [
    "Злой водитель в глухой пробке",
    "Студент в общаге, который шепчет",
    "Уставший работяга после 12-часовой смены",
    "Подросток-зумер, использующий сленг",
    "Бабушка, которая боится технологий",
    "Человек, который говорит с набитым ртом",
    "Торопящийся курьер",
    "Гопник с района",
    "Очень ленивый человек, лежащий на диване",
    "Фитнес-тренер на пробежке"
]

situations = [
    "на шумной вечеринке",
    "глубокой ночью, когда все спят",
    "работает за компьютером в наушниках",
    "моет посуду, руки мокрые",
    "во время напряженного телефонного разговора"
]
def generate(intent,person,situation):
    prompt = f"""Ты — лингвист-инженер. Сгенерируй 13 коротких, бытовых фраз для умной колонки.
    Интент: {intent}
    Кто говорит: {persona}
    Ситуация: {situation}

    ЖЁСТКИЕ ПРАВИЛА:
    1. Речевая лень: Люди говорят очень коротко. Проглатывай слова (например: 'че-то орет', 'дальше', 'некст', 'тише сделай', 'выруби', 'хорош'). 
    2. НИКАКИХ выдуманных слов (никаких "скипнад" или "допни"). Используй только реальный русский разговорный сленг или мат (зацензуренный звездочками).
    3. Добавляй слова-паразиты (ну, эээ, типа, блин, короче, алё, слышь), если это подходит персоне.
    4. Выведи ТОЛЬКО текст. Каждая фраза с новой строки.
    5. Строгий формат: фраза;{intent}

    Никаких вступлений, кавычек или нумерации."""

    data = ollama.generate(
        model = "qwen3-next:80b-cloud",
        prompt = prompt,
        options = {'temperature': 0.8},
        
    )
        
    return data.response

with open('C:\\PythonProjects\\Local Jarvis ( AI Assistant )\\model train\\mega_dataset_5k.csv', 'w', encoding='utf-8') as f:
    for intent in intents:
        for persona in personas:
            for situation in situations:
                print(f"Генерируем: {intent} | {persona} | {situation}")
                try:
                    result = generate(intent=intent,person=persona,situation=situation)
                    clean_lines = []
                    for line in result.split('\n'):
                        line = line.strip()
                        if line and ';' in line and not line.startswith('```'):
                            clean_lines.append(line)
                    f.write('\n'.join(clean_lines) + "\n")
                    f.flush()
                    time.sleep(1.5)
                except Exception as e:
                    print(f"Ошибка API: {e}")
                    time.sleep(5)

print("Генерация завершена. Сэр, датасет готов к обучению.")