import pandas as pd
import re

def cleaning(row):
  return re.sub("[^A-Za-z']+", ' ', str(row)).lower()

def get_input(inf):
  df = pd.read_csv(inf, sep="\n", header=None)
  df_clean = df.applymap(cleaning)
  return df_clean[0]
