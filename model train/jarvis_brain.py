import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification


MODEL_PATH = "Jarvis_v2\checkpoint-1791"

tokenizer = AutoTokenizer.from_pretrained("DeepPavlov/rubert-base-cased")

model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)

model.eval()

def get_intent(phrase: str) -> str:
    """Принимает текст, возвращает строковый интент"""
    
    inputs = tokenizer(phrase, return_tensors = "pt", truncation = True, max_length = 32, padding = True)
    
    with torch.no_grad():
        outputs = model(**inputs)
        
    logits = outputs.logits[0]

    probabilities = torch.sigmoid(logits)
    print(probabilities)

    detected_intents = {}
    
    # Пробегаемся по всем вероятностям
    for class_id, prob in enumerate(probabilities):
        prob_value = prob.item() # Переводим тензор в обычное число Python
        
        # Если уверенность больше 40% (порог можно менять)
        if prob_value > 0.5:
            intent_name = model.config.id2label[class_id]
            detected_intents[intent_name] = prob_value
            
    return detected_intents

# --- БЛОК ТЕСТИРОВАНИЯ ---
if __name__ == "__main__":
    print("Джарвис загружен. Жду команд (для выхода введите 'q')")
    while True:
        text = input("Вы: ")
        if text.lower() in ['q', 'й', 'exit', 'выход']:
            break
            
        intent = get_intent(text)
        print(f"-> Распознаны интенты: {intent}\n")