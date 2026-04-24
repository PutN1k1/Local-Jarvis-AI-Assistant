from transformers import AutoTokenizer
import pandas as pd

data_to_train_from_csv = pd.read_csv('model train/train_data.csv',
                                     encoding='UTF-8',
                                     delimiter=';',
                                     names=['phrase','intents']
                                     )
label2id = {}
id2label = {}
set_of_intents = set()

for intent in data_to_train_from_csv.intents:
    set_of_intents.add(intent.strip())
    
for id,intent in enumerate(set_of_intents):
    label2id[intent.strip()] = id
    id2label[id] = intent.strip()
    
data_to_train_from_csv.replace({'intents':label2id},inplace=True)
#print(data_to_train_from_csv)
    
for phrase,intent in zip(data_to_train_from_csv.phrase.head(1),data_to_train_from_csv.intents.head(1)):
    print(phrase,intent)