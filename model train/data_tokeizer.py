from transformers import AutoTokenizer
import pandas as pd
from torch.utils.data import Dataset
import torch
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

encodings = tokenizer(all_phrases,padding = True,truncation = True,return_tensors = "pt", max_length = 32)

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
        raise len(self.labels)

train_dataset = JarvisIntentDataset(encodings,all_intents)
print(train_dataset[0])