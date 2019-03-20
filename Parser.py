import pandas as pd  # For data handling
import spacy  # For preprocessing
import re  # For preprocessing
from spacy import displacy
from collections import deque

df = pd.read_csv('us.txt', sep="\n", header=None)
nlp = spacy.load('en')

def cleaning(row):
  return re.sub("[^A-Za-z']+", ' ', str(row)).lower()

def lemmatize(row):
  row = nlp(row)
  return [token.lemma_ for token in row if not token.is_stop]

df_clean = df.applymap(cleaning)
df_lemma = df_clean.applymap(lemmatize)

def phrase_traversal(t_node, p_list, filter_args = []):
  if (t_node is None) or t_node.dep_ in filter_args:
    return p_list

  for node in t_node.lefts:
    p_list = phrase_traversal(node, p_list, filter_args)

  p_list.append(t_node)

  for node in t_node.rights:
    p_list = phrase_traversal(node, p_list, filter_args)

  return p_list

def get_action_of(doc):
  root = [token for token in doc if token.head == token][0]
  act_root_list = [child for child in root.children if child.dep_=='xcomp']
  if act_root_list:
    act_root = act_root_list[0]
    phrase_list = phrase_traversal(act_root, [], ['advcl'])
    return phrase_list
  else:
    print("Can't find the action for:\n\t{}".format(doc))
    return None

def get_role_of(doc):
  root = [token for token in doc if token.head == token][0]
  role_prep_list = [child for child in root.children if child.dep_=='prep']
  if role_prep_list:
    role_prep = role_prep_list[0]
    role_subj_list = [child for child in role_prep.children if child.dep_=='pobj']
    if role_subj_list:
      role_subj = role_subj_list[0]
      return role_subj
    else:
      print("Can't find the role for:\n\t{}".format(role_prep_list))
      return None
  else:
    print("Can't find the prep for:\n\t{}".format(doc))
    return None



