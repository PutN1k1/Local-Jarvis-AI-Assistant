import pandas as pd

data_to_train_from_csv = pd.read_csv('model train/mega_dataset_5k.csv',
                                     encoding='UTF-8',
                                     delimiter=';',
                                     names=['phrase','intents']
                                     )

data_to_train_from_csv.drop_duplicates(subset=['phrase'], keep = 'first',inplace=True)
data_to_train_from_csv.to_csv( path_or_buf='model train/mega_dataset_5k.csv', sep=';',index= False, header= False)