import os
import pandas as pd



data_path = os.environ.get('DATA_PATH')

for filename in os.listdir(data_path):
    stock_name=filename.split('_')[0]
    file_path = os.path.join(data_path, filename)
    df = pd.read_csv(file_path)
    df['stock'] = stock_name
    df= df[4000:]
    df.to_csv(file_path, index=False)

