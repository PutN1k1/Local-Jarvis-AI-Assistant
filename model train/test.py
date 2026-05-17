import os
from dotenv import load_dotenv

load_dotenv()
raw_key = os.getenv("GROQ_API_KEY")

if raw_key:
    print(f"Длина ключа: {len(raw_key)} символов")
    print(f"Есть ли пробелы в начале/конце: {raw_key != raw_key.strip()}")
    print(f"Начинается на gsk_: {raw_key.startswith('gsk_')}")
    
    # Попробуем сделать запрос с очищенным ключом
    import requests
    url = "https://api.groq.com/openai/v1/models"
    headers = {
        "Authorization": f"Bearer {raw_key.strip()}",
        "Content-Type": "application/json"
    }
    res = requests.get(url, headers=headers)
    print(f"Статус ответа: {res.status_code}")
    if res.status_code != 200:
        print(f"Текст ошибки: {res.text}")
else:
    print("Ключ вообще не найден!")