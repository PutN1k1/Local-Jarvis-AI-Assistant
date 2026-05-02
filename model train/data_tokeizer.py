from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
import pandas as pd
from torch.utils.data import Dataset
import torch
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np

data_to_train_from_csv = pd.read_csv('model train/train_data.csv',
                                     encoding='UTF-8',
                                     delimiter=';',
                                     names=['phrase','intents']
                                     )
label2id = {}
id2label = {}
unique_intents = sorted(list(set(data_to_train_from_csv.intents)))

for id,intent in enumerate(unique_intents):
    label2id[intent.strip()] = id
    id2label[id] = intent.strip()

data_to_train_from_csv.replace({'intents':label2id},inplace=True)
#print(data_to_train_from_csv)

tokenizer = AutoTokenizer.from_pretrained("cointegrated/rubert-tiny2")

'''for phrase,intent in zip(data_to_train_from_csv.phrase.head(1),data_to_train_from_csv.intents.head(1)):
    print(phrase,intent)
    encoded_phrase = tokenizer(phrase)
    print(encoded_phrase)'''
    
'''pharses = list(data_to_train_from_csv.phrase.head(5))
encoded_phrases = tokenizer(pharses, padding = True,truncation = True,return_tensors = "pt")
print(encoded_phrases['input_ids'])
print(encoded_phrases['token_type_ids'])
print(encoded_phrases['attention_mask'])'''

all_phrases = data_to_train_from_csv['phrase'].tolist()
all_intents = data_to_train_from_csv['intents'].tolist()

train_texts, eval_texts, train_labels, eval_labels = train_test_split(all_phrases,all_intents,train_size=0.8,random_state=42, stratify=all_intents)

#print(np.bincount(train_labels))
#print(np.bincount(eval_labels))

encodings_train = tokenizer(train_texts,padding = True,truncation = True,return_tensors = "pt", max_length = 32)
encodings_eval = tokenizer(eval_texts,padding = True,truncation = True,return_tensors = "pt", max_length = 32)

'''for key, val in encodings.items():
    item = {key : val[0]for key, val in encodings.items()}
print(item)'''

class JarvisIntentDataset(Dataset):
    def __init__(self,encodings, labels):
        self.encodings = encodings
        self.labels = labels
    
    def __getitem__(self, idx):
        item = {key : val[idx] for key, val in self.encodings.items()}
        
        item['labels'] = torch.tensor(self.labels[idx])
        
        return item
    
    def __len__(self):
        return len(self.labels)


model = AutoModelForSequenceClassification.from_pretrained("cointegrated/rubert-tiny2", num_labels=8, id2label=id2label, label2id=label2id)

train_dataset = JarvisIntentDataset(encodings_train,train_labels)
eval_dataset = JarvisIntentDataset(encodings_eval,eval_labels)

def compute_metrics(eval_pred):
    logits,labels = eval_pred
    predictions = np.argmax(logits,axis = -1)
    
    acc = accuracy_score(labels,predictions)
    return {"accuracy": acc}

 
training_args = TrainingArguments(
    output_dir="Jarvis_v1",
    learning_rate=5e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=30,
    weight_decay=0.01,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    compute_metrics= compute_metrics
)

trainer.train()
