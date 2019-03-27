import spacy  # For preprocessing
import re  # For preprocessing

nlp = spacy.load('en_core_web_md')


def cleaning(row):
  return re.sub("[^A-Za-z']+", ' ', str(row)).lower()


def lemmatize(row):
  row = nlp(row)
  return [token.lemma_ for token in row if not token.is_stop]


def phrase_traversal(t_node, p_list, filter_args=[]):
  if (t_node is None) or t_node.dep_ in filter_args:
    return p_list

  for node in t_node.lefts:
    p_list = phrase_traversal(node, p_list, filter_args)

  p_list.append(t_node)

  for node in t_node.rights:
    p_list = phrase_traversal(node, p_list, filter_args)

  return p_list


def get_action_of(doc, idx=0):
  root = [token for token in doc if token.has_vector and token.similarity(nlp('want')) >= 0.9][0]
  act_root_list = [child for child in root.children if child.dep_ in ['xcomp', 'dobj', 'ccomp']]
  if act_root_list:
    act_root = act_root_list[0]
    phrase_list = phrase_traversal(act_root, [], ['advcl'])
    return ' '.join([str(e.text) for e in phrase_list])
  else:
    print("{} Can't find the action for:\n\t{}".format(idx, doc))
    return None


def get_role_of(doc):
  root = [token for token in doc if token.has_vector and token.similarity(nlp('as')) >= 0.9][0]
  if root:
    role_subj_list = [child for child in root.children if child.dep_=='pobj']
    if role_subj_list:
      role_subj = role_subj_list[0]
      role_compound_list = [e for e in role_subj.lefts if e.dep_ == 'compound'] + [role_subj] + [e for e in role_subj.rights if e.dep_ == 'compound']
      return ' '.join([str(e.text) for e in role_compound_list])
    else:
      print("Can't find the role for:\n\t{}".format(root))
      return None
  else:
    print("Can't find the prep for:\n\t{}".format(doc))
    return None
