import pandas as pd

a = "dataset/dataset.xlsx"

df = pd.read_excel(a)

df.to_csv('output/company_list.csv')


