import random
import IO
import os
from subprocess import call


def get_oms_out():
  return os.popen('./optimathsat/bin/optimathsat < output.txt').read()

def get_graph():
  return os.popen('dot graph.dot -Tpng -o graph.jpg')



def contains(the_list, custom_filter):
  for x in the_list:
    if custom_filter(x):
      return True
  return False


class US2SMT:

  def __init__(self, in_file, parser):
    self.parser = parser
    self.in_file = in_file
    self.refinement_id = 0
    self.goal_id = 0

    self.user_stories = []
    self.goals = []
    self.refinements = []

    self.smt = ''
    self.graph = ''
    self.goal_set = ''

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
      self.pWeight = []
      self.nWeight = []
      self.content = None

  # a = UserStory(1)
  # b = UserStory(2)
  # c = UserStory(3)
  #
  # a.role = 'publisher'
  # a.action = 'sign up'
  # a.pWeight.append(('pos', 3))
  # a.nWeight.append(('eff', 2))
  # b.role = 'publisher'
  # b.action = 'publish'
  # b.pWeight.append(('pos', 10))
  # b.nWeight.append(('eff', 1))
  # c.role = 'admin'
  # c.action = 'create profile'
  # c.pWeight.append(('pos', 4))
  # c.nWeight.append(('eff', 2))

  # user_stories.append(a)
  # user_stories.append(b)
  # user_stories.append(c)

  def get_smt_input(self):
    clean_input = IO.get_input(self.in_file)
    refinement_id = self.refinement_id
    goal_id = self.goal_id

    user_stories = self.user_stories
    goals = self.goals
    refinements = self.refinements

    smt = self.smt
    graph = self.graph
    goal_set = self.goal_set

    for idx, us in enumerate(clean_input):
      tmp_us = self.UserStory(idx)
      tmp_us.content = us
      tmp_us.role = self.parser.get_role_of(self.parser.nlp(us))
      tmp_us.action = self.parser.get_action_of(self.parser.nlp(us))
      tmp_us.pWeight.append(('gain', random.randint(0, 20)))
      tmp_us.pWeight.append(('attr', random.randint(0, 10)))
      tmp_us.nWeight.append(('effort', random.randint(0, 5)))
      if tmp_us.action is not None and tmp_us.role is not None:
        user_stories.append(tmp_us)

    for u in user_stories:
      if contains(goals, lambda g: g.name == u.role):
        new_goal = self.Goal(goal_id)
        goal_set += 'G' + str(goal_id) + ' : ' + u.action + '\r\n'
        goal_id += 1
        new_goal.set_leaf()
        for p in u.pWeight:
          new_goal.pWeight.append(p)
        for n in u.nWeight:
          new_goal.nWeight.append(n)
        new_goal.name = u.action
        goals.append(new_goal)
        new_ref = self.Refinement(refinement_id)
        refinement_id += 1
        new_ref.children.append(new_goal)
        new_ref.parent = list(filter(lambda g: g.name == u.role, goals))[0].id_
        list(filter(lambda g: g.name == u.role, goals))[0].children.append(new_ref)
        refinements.append(new_ref)
      else:
        new_goal = self.Goal(goal_id)
        goal_id += 1
        new_goal.set_root()
        new_goal.set_mandatory()
        new_goal.name = u.role
        goals.append(new_goal)
        new_ref = self.Refinement(refinement_id)
        refinement_id += 1
        new_ref.parent = new_goal.id_
        new_goal.children.append(new_ref)
        new_goal = self.Goal(goal_id)
        goal_set += 'G' + str(goal_id) + ' : ' + u.action + '\r\n'
        goal_id += 1
        new_goal.set_leaf()
        for p in u.pWeight:
          new_goal.pWeight.append(p)
        for n in u.nWeight:
          new_goal.nWeight.append(n)
        new_goal.name = u.action
        goals.append(new_goal)
        new_ref.children.append(new_goal)
        refinements.append(new_ref)

    smt += '(set-option :produce-models true)\r\n(set-option :opt.priority lex)\r\n\r\n'
    graph += 'digraph G {\r\n'


    for g in goals:
      smt += '(declare-fun ' + g.id_ + ' () Bool) \r\n'
      if g.isMandatory:
        smt += '(assert ' + g.id_ + ')\r\n(assert-soft ' + g.id_ + ' :id unsat_requirements)\r\n'

    for r in refinements:
      smt += '(declare-fun ' + r.id_ + ' () Bool) \r\n'

    for g in goals:
      if not g.isLeaf:
        smt += '(assert (=> ' + g.id_ + '(or '
        for c in g.children:
          graph += '\t' + g.id_ + ' -> ' + c.id_ + ';\r\n'
          graph += c.id_ + ' [shape=circle,style=filled,color=black,label=""];'
          smt += c.id_ + ' '
        smt += ')))\r\n'

    for r in refinements:
      smt += '(assert (and (= ' + r.id_ + ' (and '
      for c in r.children:
        smt += c.id_ + ' '
        graph += '\t' + r.id_ + ' -> ' + c.id_ + ';\r\n'
      smt += ')) (=> ' + r.id_ + ' ' + r.parent + ' )))\r\n'

    for g in goals:
      if g.isLeaf:
        smt += '(assert-soft (not ' + g.id_ + ' ) :id sat_tasks)\r\n'
        for p in g.pWeight:
          smt += '(assert-soft ' + g.id_ + ' :weight ' + str(p[1]) + ' :id ' + p[0] + ')\r\n'
        for n in g.nWeight:
          smt += '(assert-soft ' + g.id_ + ' :weight ' + str(n[1]) + ' :id ' + n[0] + ')\r\n'

    for p in user_stories[0].pWeight:
      smt += '(maximize ' + p[0] + ')\r\n'
    for n in user_stories[0].nWeight:
      smt += '(minimize ' + n[0] + ')\r\n'

    smt += '(minimize unsat_requirements)\r\n(minimize sat_tasks)\r\n(check-sat)\r\n'
    smt += '(get-objectives)\r\n(load-objective-model 1)\r\n(get-model)\r\n(exit)'
    graph += '}'

    f = open("output.txt", "w")
    f.write(smt)

    f2 = open("goal_set.txt", "w")
    f2.write(goal_set)

    f3 = open("graph.dot", "w")
    f3.write(graph)

    return smt, goal_set
