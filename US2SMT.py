import os
from graphviz import Digraph
import time


def get_oms_out():
  return os.popen('./optimathsat/bin/optimathsat < output.txt').read()


def contains(the_list, custom_filter):
  for x in the_list:
    if custom_filter(x):
      return True
  return False


class US2SMT:
  def __init__(self, in_file, parser, opt, opt2, max_):
    self.parser = parser
    self.opt = opt
    self.opt2 = opt2
    self.in_file = in_file
    self.refinement_id = 0
    self.goal_id = 0
    self.max_ = max_

    self.user_stories = []
    self.goals = []
    self.refinements = []

    self.smt = ''
    self.dot = Digraph()
    self.dictn = {}

  class Refinement:
    def __init__(self, id_):
      self.id_ = 'R' + str(id_)
      self.children = []
      self.parent = None

  class Goal:
    def __init__(self, id_):
      self.id_ = 'G' + str(id_)
      self.name = None
      self.isMandatory = False
      self.isRoot = False
      self.isLeaf = False
      self.children = []
      self.pWeight = []
      self.nWeight = []

    def set_mandatory(self):
      self.isMandatory = True

    def set_root(self):
      self.isRoot = True

    def set_leaf(self):
      self.isLeaf = True

  class UserStory:
    def __init__(self, id_):
      self.id_ = id_
      self.role = None
      self.action = None
      self.reason = None
      self.topic = None
      self.topic_id = None
      self.weight = []
      self.pWeight = []
      self.nWeight = []
      self.content = None
      self.act_verb = None
      self.act_obj = None

  def get_relations(self, type, level):
    if level == 2:
      dot, dictn = self.or_(type)
    else:
      dot, dictn = self.and_(type)
    return dot, dictn

  def and_(self, type):
    refinement_id = self.refinement_id
    goal_id = self.goal_id
    dictn = self.dictn
    dot = self.dot

    for u in self.user_stories:
      if type == 2:
        up = u.role
        dw = u.topic
      else:
        up = u.role
        dw = u.act_verb
      nm = up + "_" + dw
      if contains(self.goals, lambda g: g.name == nm):
        new_goal = self.Goal(goal_id)
        dictn['G' + str(goal_id)] = u.action
        dot.node(new_goal.id_, u.action)
        goal_id += 1
        new_goal.set_leaf()
        for p in u.pWeight:
          new_goal.pWeight.append(p)
        for n in u.nWeight:
          new_goal.nWeight.append(n)
        new_goal.name = u.action
        self.goals.append(new_goal)
        new_ref = self.Refinement(refinement_id)
        dot.node(new_ref.id_, shape='point')
        refinement_id += 1
        new_ref.children.append(new_goal)
        new_ref.parent = list(filter(lambda g: g.name == nm, self.goals))[0].id_
        list(filter(lambda g: g.name == nm, self.goals))[0].children.append(new_ref)
        self.refinements.append(new_ref)
      elif contains(self.goals, lambda g: g.name == up):
        new_goal = self.Goal(goal_id)
        dictn['G' + str(goal_id)] = nm
        dot.node(new_goal.id_, dw)
        goal_id += 1
        new_goal.name = nm
        self.goals.append(new_goal)
        g_id = list(filter(lambda g: g.name == up, self.goals))[0].id_
        new_ref = list(filter(lambda r: r.parent == g_id, self.refinements))[0]
        new_ref.children.append(new_goal)
        new_goal = self.Goal(goal_id)
        dictn['G' + str(goal_id)] = u.action
        dot.node(new_goal.id_, u.action)
        goal_id += 1
        new_goal.set_leaf()
        for p in u.pWeight:
          new_goal.pWeight.append(p)
        for n in u.nWeight:
          new_goal.nWeight.append(n)
        new_goal.name = u.action
        self.goals.append(new_goal)
        new_ref = self.Refinement(refinement_id)
        dot.node(new_ref.id_, shape='point')
        refinement_id += 1
        new_ref.children.append(new_goal)
        new_ref.parent = list(filter(lambda g: g.name == nm, self.goals))[0].id_
        list(filter(lambda g: g.name == nm, self.goals))[0].children.append(new_ref)
        self.refinements.append(new_ref)
      else:
        new_goal = self.Goal(goal_id)
        dictn['G' + str(goal_id)] = up
        dot.node(new_goal.id_, up)
        goal_id += 1
        new_goal.set_root()
        new_goal.set_mandatory()
        new_goal.name = up
        self.goals.append(new_goal)
        new_ref = self.Refinement(refinement_id)
        dot.node(new_ref.id_, shape='point')
        refinement_id += 1
        new_ref.parent = new_goal.id_
        new_ref.name = nm
        self.refinements.append(new_ref)
        new_goal.children.append(new_ref)
        new_goal = self.Goal(goal_id)
        dictn['G' + str(goal_id)] = nm
        dot.node(new_goal.id_, dw)
        goal_id += 1
        new_goal.name = nm
        self.goals.append(new_goal)
        g_id = list(filter(lambda g: g.name == up, self.goals))[0].id_
        new_ref = list(filter(lambda r: r.parent == g_id, self.refinements))[0]
        new_ref.children.append(new_goal)
        new_goal = self.Goal(goal_id)
        dictn['G' + str(goal_id)] = u.action
        dot.node(new_goal.id_, u.action)
        goal_id += 1
        new_goal.set_leaf()
        for p in u.pWeight:
          new_goal.pWeight.append(p)
        for n in u.nWeight:
          new_goal.nWeight.append(n)
        new_goal.name = u.action
        self.goals.append(new_goal)
        new_ref = self.Refinement(refinement_id)
        dot.node(new_ref.id_, shape='point')
        refinement_id += 1
        new_ref.children.append(new_goal)
        new_ref.parent = list(filter(lambda g: g.name == nm, self.goals))[0].id_
        list(filter(lambda g: g.name == nm, self.goals))[0].children.append(new_ref)
        self.refinements.append(new_ref)
    return dot, dictn

  def or_(self, type):
    refinement_id = self.refinement_id
    goal_id = self.goal_id
    dictn = self.dictn
    dot = self.dot
    for u in self.user_stories:
      if type == 1:
        rl = u.role
      elif type == 2:
        rl = u.topic
      else:
        rl = u.act_verb
      if contains(self.goals, lambda g: g.name == rl):
        new_goal = self.Goal(goal_id)
        dictn['G' + str(goal_id)] = u.action
        dot.node(new_goal.id_, u.action)
        goal_id += 1
        new_goal.set_leaf()
        for p in u.pWeight:
          new_goal.pWeight.append(p)
        for n in u.nWeight:
          new_goal.nWeight.append(n)
        new_goal.name = u.action
        self.goals.append(new_goal)
        new_ref = self.Refinement(refinement_id)
        dot.node(new_ref.id_, shape='point')
        refinement_id += 1
        new_ref.children.append(new_goal)
        new_ref.parent = list(filter(lambda g: g.name == rl, self.goals))[0].id_
        list(filter(lambda g: g.name == rl, self.goals))[0].children.append(new_ref)
        self.refinements.append(new_ref)
      else:
        new_goal = self.Goal(goal_id)
        dictn['G' + str(goal_id)] = rl
        dot.node(new_goal.id_, rl)
        goal_id += 1
        new_goal.set_root()
        new_goal.set_mandatory()
        new_goal.name = rl
        self.goals.append(new_goal)
        new_ref = self.Refinement(refinement_id)
        dot.node(new_ref.id_, shape='point')
        refinement_id += 1
        new_ref.parent = new_goal.id_
        new_goal.children.append(new_ref)
        new_goal = self.Goal(goal_id)
        dictn['G' + str(goal_id)] = u.action
        dot.node(new_goal.id_, u.action)
        goal_id += 1
        new_goal.set_leaf()
        for p in u.pWeight:
          new_goal.pWeight.append(p)
        for n in u.nWeight:
          new_goal.nWeight.append(n)
        new_goal.name = u.action
        self.goals.append(new_goal)
        new_ref.children.append(new_goal)
        self.refinements.append(new_ref)
    return dot, dictn

  def weight(self):
    ws = self.max_.split(',')
    for s in self.user_stories:
      for w in s.weight:
        if contains(ws, lambda ws: ws == w[0]):
          s.pWeight.append(w)
        else:
          s.nWeight.append(w)
    return self

  def add_us(self):
    t_start = time.time()
    processed_df = self.parser.get_input(self.in_file)
    t_end = time.time()
    print('Parser time: {}'.format(t_end-t_start))
    known_cols = ['clean', 'doc', 'act_tokenized', 'act_span', 'User Story', 'role',
                  'topic_id', 'topic_kw', 'act_verb', 'act_obj']
    weight_cols = [col for col in processed_df.columns if col not in known_cols]
    for idx, us in processed_df.iterrows():
      tmp_us = self.UserStory(idx)
      tmp_us.content = us['User Story']
      tmp_us.role = us['role'] if us['role'] else 'other'
      tmp_us.action = us['act_span'].text if us['act_span'] else 'other'
      tmp_us.act_verb = us['act_verb'].text if us['act_verb'] else 'other'
      tmp_us.act_obj = us['act_obj'] if us['act_obj'] else 'other'
      tmp_us.topic_id = us['topic_id'] if us['topic_id'] else 'other'
      tmp_us.topic = us['topic_kw'] if us['topic_kw'] else 'other'
      tmp_us.weight = [(col, us[col]) for col in weight_cols]
      if tmp_us.action is not None and tmp_us.role is not None:
        if contains(self.user_stories, lambda s: s.role == tmp_us.role and s.action == tmp_us.action):
          continue
        self.user_stories.append(tmp_us)
    return self

  def get_smt_input(self):
    smt = self.smt
    if self.opt2 == '1':
      dot, dictn = self.get_relations(1, 2)
    elif self.opt2 == '2':
      dot, dictn = self.get_relations(2, 2)
    elif self.opt2 == '3':
      dot, dictn = self.get_relations(2, 3)
    elif self.opt2 == '4':
      dot, dictn = self.get_relations(3, 2)
    else:
      dot, dictn = self.get_relations(3, 3)

    smt += '(set-option :produce-models true)\r\n'

    if self.opt == '1':
      smt += '(set-option :opt.priority box)\r\n\r\n'
    elif self.opt == '2':
      smt += '(set-option :opt.priority lex)\r\n\r\n'
    else:
      smt += '(set-option :opt.priority pareto)\r\n\r\n'

    for g in self.goals:
      smt += '(declare-fun ' + g.id_ + ' () Bool) \r\n'
      if g.isMandatory:
        smt += '(assert ' + g.id_ + ')\r\n(assert-soft ' + g.id_ + ' :id unsat_requirements)\r\n'

    for r in self.refinements:
      smt += '(declare-fun ' + r.id_ + ' () Bool) \r\n'

    # or
    for g in self.goals:
      if not g.isLeaf:
        smt += '(assert (=> ' + g.id_ + '(or '
        for c in g.children:
          dot.edge(g.id_, c.id_, dir='back')
          smt += c.id_ + ' '
        smt += ')))\r\n'

    # and
    for r in self.refinements:
      smt += '(assert (and (= ' + r.id_ + ' (and '
      for c in r.children:
        smt += c.id_ + ' '
        dot.edge(r.id_, c.id_, dir='back')
      smt += ')) (=> ' + r.id_ + ' ' + r.parent + ' )))\r\n'

    for g in self.goals:
      if g.isLeaf:
        smt += '(assert-soft (not ' + g.id_ + ' ) :id sat_tasks)\r\n'
        for p in g.pWeight:
          smt += '(assert-soft (not ' + g.id_ + ' ) :weight ' + str(p[1]) + ' :id ' + p[0] + ')\r\n'
        for n in g.nWeight:
          smt += '(assert-soft (not ' + g.id_ + ' ) :weight ' + str(n[1]) + ' :id ' + n[0] + ')\r\n'

    smt += '(minimize unsat_requirements)\r\n(minimize sat_tasks)\r\n'
    ws = self.max_.split(',')
    for w in self.user_stories[0].weight:

      if contains(ws, lambda m: m == w[0]):
        smt += '(maximize ' + w[0] + ')\r\n'
      else:
        smt += '(minimize ' + w[0] + ')\r\n'

    smt += '(check-sat)\r\n'
    smt += '(get-objectives)\r\n(load-objective-model 1)\r\n(get-model)\r\n(exit)'

    f = open("output.txt", "w")
    f.write(smt)

    return smt, dot, dictn
