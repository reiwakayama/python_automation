# Get hashed email address

import hashlib
import pandas as pd

def sha256(s: str): 
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

df = pd.read_excel(r"C:\Users\81701\python\hashemail.xlsx")
# hashemail.xlsx should just have 1 column "Email" with list of clean email addresses

df['Email'] = df['Email'].str.strip()
df['Email'] = df['Email'].str.lower()
df['Email' ] = df['Email'].apply(sha256)

# pd.set_option('display.max_columns', None)

# print(df)
print(df.iloc[0, 0])
