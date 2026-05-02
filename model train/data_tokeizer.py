from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
import pandas as pd
from torch.utils.data import Dataset
import torch
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy

data_to_train_from_csv = pd.read_csv('model train/train_data.csv',
                                     encoding='UTF-8',
                                     delimiter=';',
                                     names=['phrase','intents']
                                     )
label2id = {}
id2label = {}

all_raw_intents = data_to_train_from_csv.intents.astype(str).tolist()
unique_intents = set()
for item in all_raw_intents:
    for i in item.split(','):
        unique_intents.add(i.strip())

unique_intents = sorted(list(unique_intents))

for id,intent in enumerate(unique_intents):
    label2id[intent.strip()] = id
    id2label[id] = intent.strip()

def get_one_hot_labels(intent_string,label2id,num_lables = 8):
    one_hot = [0.0] * num_lables
    for intent in str(intent_string).split(','):
        intent = intent.strip()
        if intent in label2id:
            one_hot[label2id[intent]] = 1.0
    return one_hot

tokenizer = AutoTokenizer.from_pretrained("DeepPavlov/rubert-base-cased")

all_phrases = data_to_train_from_csv['phrase'].tolist()
all_intents = [get_one_hot_labels(x,label2id) for x in data_to_train_from_csv['intents']]

train_texts, eval_texts, train_labels, eval_labels = train_test_split(all_phrases,all_intents,train_size=0.8,random_state=42)


encodings_train = tokenizer(train_texts,padding = True,truncation = True,return_tensors = "pt", max_length = 32)
encodings_eval = tokenizer(eval_texts,padding = True,truncation = True,return_tensors = "pt", max_length = 32)

'''for key, val in encodings_train.items():
    
    item = {key : val[0]for key, val in encodings_train.items()}
print(item)'''

class JarvisIntentDataset(Dataset):
    def __init__(self,encodings, labels):
        self.encodings = encodings
        self.labels = labels
    
    def __getitem__(self, idx):
        item = {key : val[idx] for key, val in self.encodings.items()}
        
        item['labels'] = torch.tensor(self.labels[idx],dtype=torch.float32)
        
        return item
    
    def __len__(self):
        return len(self.labels)


model = AutoModelForSequenceClassification.from_pretrained(
    "DeepPavlov/rubert-base-cased", 
    num_labels=8, 
    id2label=id2label, 
    label2id=label2id,
    problem_type = "multi_label_classification"
)

train_dataset = JarvisIntentDataset(encodings_train,train_labels)
eval_dataset = JarvisIntentDataset(encodings_eval,eval_labels)

def compute_metrics(eval_pred):
    logits,labels = eval_pred
    
    probabilities = torch.sigmoid(torch.tensor(logits)).numpy()
    
    predictions = (probabilities > 0.5).astype(int)
    
    acc = accuracy_score(labels,predictions)
    return {"accuracy": acc}

training_args = TrainingArguments(
    output_dir="Jarvis_v2",
    learning_rate=5e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=10,
    weight_decay=0.1,
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
