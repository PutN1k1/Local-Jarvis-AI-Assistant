import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np

MODEL_PATH = "Jarvis_v1\checkpoint-1020"

tokenizer = AutoTokenizer.from_pretrained("cointegrated/rubert-tiny2")

model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)

model.eval()

def get_intent(phrase: str) -> str:
    """Принимает текст, возвращает строковый интент"""
    
    inputs = tokenizer(phrase, return_tensors = "pt", truncation = True, max_length = 32, padding = True)
    
    with torch.no_grad():
        outputs = model(**inputs)
        
    logits = outputs.logits
    
    predicted_class_id = np.argmax(logits.numpy(), axis=-1)[0]
    
    intent = model.config.id2label[predicted_class_id]
    
    return intent

# --- БЛОК ТЕСТИРОВАНИЯ ---
if __name__ == "__main__":
    print("Джарвис загружен. Жду команд (для выхода введите 'q')")
    while True:
        text = input("Вы: ")
        if text.lower() in ['q', 'й', 'exit', 'выход']:
            break
            
        intent = get_intent(text)
        print(f"-> Распознан интент: [{intent}]\n")