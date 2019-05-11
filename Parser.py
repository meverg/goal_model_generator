import pandas as pd
import re
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation, TruncatedSVD


def cleaning(row):
  return re.sub("[^A-Za-z']+", ' ', str(row)).lower()


def sort_topics(topic_probs):
  all_topics = [d.argmax() for d in topic_probs]
  return sorted(set(all_topics), key=all_topics.count, reverse=True)


class Parser:

  def __init__(self, nlp, model_selection='LDA', vectorizer_selection='COUNT'):
    self.vectorizer_selection = vectorizer_selection  # COUNT or TFIDF
    self.model_selection = model_selection  # LDA or NNMF or LSI
    self.nlp = nlp
    self.punctuations = punctuation
    self.stopwords = list(STOP_WORDS)
    self.data_vectorized = None
    self.vectorizer = None
    self.df = None
    self.model = None
    self.modeled_data = None
    self.topic_kw_dict = {}

  def get_input(self, inf):
    self.df = pd.read_csv(inf)
    self.df['clean'] = self.df['User Story'].apply(cleaning)
    self.df['doc'] = self.df['clean'].apply(self.nlp)
    self.df['role'] = self.df['doc'].apply(self.get_role_of)
    self.df['act'] = self.df['doc'].apply(self.get_action_of).apply(lambda x: re.sub(r'^to ', '', x))
    self.df['act_tokenized'] = self.df['act'].apply(self.spacy_tokenizer)
    self.df['act_verb'] = self.df['doc'].apply(self.get_verb_token_of)
    self.df['act_obj'] = self.df['verb'].apply(self.get_action_obj_of)
    self.vectorize()
    self.extract_topics()
    self.df['topic_id'] = [self.modeled_data[i].argmax() for i in range(self.modeled_data.shape[0])]
    self.build_topic_kw_dict()
    self.df['topic_kw_list'] = self.df['topic_id'].apply(self.topic_kw_dict.get)
    return self.df

  # noinspection SpellCheckingInspection
  # def lemmatize(self, row):
  #   row = self.nlp(row)
  #   return [token.lemma_ for token in row if not token.is_stop]

  def phrase_traversal(self, t_node, p_list, filter_args=[]):
    if (t_node is None) or t_node.dep_ in filter_args:
      return p_list

    for node in t_node.lefts:
      p_list = self.phrase_traversal(node, p_list, filter_args)

    p_list.append(t_node)

    for node in t_node.rights:
      p_list = self.phrase_traversal(node, p_list, filter_args)

    return p_list

  def get_action_of(self, doc, idx=0):
    try:
      root = [token for token in doc if token.has_vector and token.similarity(self.nlp('want')) >= 0.9][0]
      act_root_list = [child for child in root.children if child.dep_ in ['xcomp', 'dobj', 'ccomp']]
      if act_root_list:
        act_root = act_root_list[0]
        phrase_list = self.phrase_traversal(act_root, [], ['advcl'])
        return ' '.join([str(e.text) for e in phrase_list])
      else:
        print("{} Can't find the action for:\n\t{}".format(idx, doc))
        return None
    except Exception as E:
      print("Couldn't get action of:\n {}\n {}".format(doc, E))
      return None

  def get_role_of(self, doc):
    try:
      root = [token for token in doc if token.has_vector and token.similarity(self.nlp('as')) >= 0.9][0]
      if root:
        role_subj_list = [child for child in root.children if child.dep_ == 'pobj']
        if role_subj_list:
          role_subj = role_subj_list[0]
          role_compound_list = [e for e in role_subj.lefts if e.dep_ == 'compound'] + [role_subj] + [e for e in
                                                                                                     role_subj.rights if
                                                                                                     e.dep_ == 'compound']
          return ' '.join([str(e.text) for e in role_compound_list])
        else:
          print("Can't find the role for:\n\t{}".format(root))
          return None
      else:
        print("Can't find the prep for:\n\t{}".format(doc))
        return None
    except Exception as E:
      print("Couldn't get role of:\n {}\n {}".format(doc, E))
      return None

  def get_verb_token_of(self, doc):
    root = [token for token in doc if token.has_vector and token.similarity(self.nlp('want')) >= 0.9][0]
    act_root_list = [child for child in root.children if child.pos_ == 'VERB']
    if act_root_list:
      if len(act_root_list) > 1:
        return [act_root for act_root in act_root_list if act_root.dep_ in ['xcomp', 'dobj', 'ccomp']][0]
      else:
        return act_root_list[0]
    else:
      print("Can't find the act verb for:\n\t{}".format(doc))
      return None

  def get_action_obj_of(self, verb):
    obj_list = [child for child in verb.children if child.dep_ == 'dobj']
    if obj_list:
      dobj = obj_list[0]
      dobj_compound_list = [e for e in dobj.lefts if e.dep_ == 'compound'] + [dobj] + [e for e in dobj.rights if
                                                                                       e.dep_ == 'compound']
      return ' '.join([str(e.text) for e in dobj_compound_list])
    else:
      print("Can't find the act obj for:\n\t{}".format(verb))
      return None

  def spacy_tokenizer(self, sentence):
    if sentence is None:
      return None
    my_tokens = self.nlp(sentence)
    my_tokens = [word.lemma_.lower().strip() if word.lemma_ != "-PRON-" else word.lower_ for word in my_tokens]
    my_tokens = [word for word in my_tokens if word not in self.stopwords and word not in self.punctuations]
    my_tokens = " ".join([i for i in my_tokens])
    return my_tokens

  def vectorize(self):
    if self.vectorizer_selection == 'COUNT':
      self.vectorizer = CountVectorizer(min_df=2, max_df=0.95, stop_words='english')
    elif self.vectorizer_selection == 'TFIDF':
      self.vectorizer = TfidfVectorizer(min_df=2, max_df=0.95, stop_words='english')
    else:
      raise ValueError('wrong vectorizer selection')
    self.data_vectorized = self.vectorizer.fit_transform(self.df['act_tokenized'])

  def extract_topics(self):
    num_topics = len(self.df['act_tokenized'])
    if self.model_selection == 'LDA':
      self.model = LatentDirichletAllocation(n_components=num_topics, learning_method='online')
    elif self.model_selection == 'NNMF':
      self.model = NMF(n_components=num_topics)
    elif self.model_selection == 'LSI':
      self.model = TruncatedSVD(n_components=min(num_topics, len(self.vectorizer.get_feature_names()) - 1))
    else:
      raise ValueError('wrong model selection')

    self.modeled_data = self.model.fit_transform(self.data_vectorized)

  def top_n_kw_of_topic(self, topic_id, top_n=1):
    topic = self.model.components_[topic_id]
    return [self.vectorizer.get_feature_names()[i] for i in topic.argsort()[:-top_n - 1:-1]]

  def build_topic_kw_dict(self):
    used_kws = []
    topic_kw_dict = {}
    for topic_id in sort_topics(self.modeled_data):
      tmp_kws = [kw for kw in (self.top_n_kw_of_topic(topic_id)) if kw not in used_kws]
      topic_kw_dict[topic_id] = tmp_kws
      used_kws.extend(tmp_kws)
    self.topic_kw_dict = topic_kw_dict
