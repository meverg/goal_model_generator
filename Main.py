import re
import Parser

refinementId = 0
goalId = 0

def contains(list, filter):
    for x in list:
        if filter(x):
            return True
    return False

class Refinement:
	def __init__(self, id_):
		self.id_ = 'R' +id_
		self.childs = []
		self.parent

class Goal:
	def __init__(self, id_):
		self.id_ = 'G' + id_
		self.name
		self.isMandatory = False
		self.isRoot = False
		self.isLeaf = False
		self.childs = []
	def setMandatory(self):
		self.isMandatory = True
	def setRoot(self):
		self.isRoot = True
	def setLeaf(self):
		self.isLeaf = True

class UserStory:
	def __init__(self, id_):
		self.id_ = id_
		self.text
		self.role
		self.action
		self.reason
		self.weight = []
		self.content = None

userStories = []
goals = []
refinements = []

for idx, us in enumerate(Parser.df_clean[0]):
	tmp_us = UserStory(idx)
	tmp_us.text = us
	tmp_us.role = Parser.get_role_of(Parser.nlp(us))
	tmp_us.role = Parser.get_action_of(Parser.nlp(us))
	userStories.append(tmp_us)



for u in userStories:
	if contains(goals, lambda g: g.name == u.role):
		newGoal = Goal(goalId)
		goalId += 1
		newGoal.setLeaf()
		newGoal.name = u.action
		goals.append(newGoal)
		newRef = Refinement(refinementId)
		refinementId += 1
		newRef.childs.append(newGoal)
		newRef.parent = goals(filter(lambda g: g.name == u.role))[0].id_
	else:
		newGoal = Goal(goalId)
		goalId += 1
		newGoal.setRoot()
		newGoal.setMandatory()
		newGoal.name = u.role
		goals.append(newGoal)
		newRef = Refinement(refinementId)
		refinementId += 1
		newRef.parent = newGoal.name
		newGoal = Goal(goalId)
		goalId += 1
		newGoal.setLeaf()
		newGoal.name = u.action
		goals.append(newGoal)
		newRef.childs.append(newGoal)



smt = '(set-option :produce-models true)\r\n(set-option :opt.priority lex)\r\n\r\n'

for g in goals:
	smt += '(declare-fun ' + g.id_ + ' () Bool) \r\n'
	if g.isMandatory:
		smt += '(assert ' + g.id_ + ')\r\n(assert-soft ' + g.id_ +' :id unsat_requirements)\r\n'

for r in refinements:
	smt += '(declare-fun ' + r.id_ + ' () Bool) \r\n'

for g in goals:
	if not g.isLeaf:
		smt += '(assert (=> ' + g.id_ + '(or '
		for c in g.childs:
			smt += c + ' '
		smt += ')))\r\n'

for r in refinements:
	smt += '(assert (and (= ' + r.id_ + ' (and '
	for c in r.childs:
		smt += c + ' '
	smt += ')) (=> ' + r.id_ + ' ' + r.parent + ' )))\r\n'

for g in goals:
	if g.isLeaf:
		smt += '(assert-soft (not ' + g.id_ +' ) :id sat_tasks)\r\n'

smt += '(minimize unsat_requirements)\r\n(minimize sat_tasks)\r\n(check-sat)\r\n(get-objectives)\r\n(load-objective-model 1)\r\n(get-model)\r\n(exit)'

print(smt)