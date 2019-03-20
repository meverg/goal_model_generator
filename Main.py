import re

refinementId = 0
goalId = 0

def contains(list, filter):
    for x in list:
        if filter(x):
            return True
    return False

class Refinement:
	def __init__(self, id_):
		self.id_ = 'R' + str(id_)
		self.childs = []
		self.parent = None

class Goal:
	def __init__(self, id_):
		self.id_ = 'G' + str(id_)
		self.name = None
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
		self.role = None
		self.action = None
		self.reason = None
		self.weight = []
		self.content = None

a = UserStory(1)
b = UserStory(2)
c = UserStory(3)

a.role = 'publisher'
a.action = 'sign up'
b.role = 'publisher'
b.action = 'publish'
c.role = 'admin'
c.action = 'create profile'


userStories = []
goals = []
refinements = []

userStories.append(a)
userStories.append(b)
userStories.append(c)

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
		newRef.parent = list(filter(lambda g: g.name == u.role, goals))[0].id_
		list(filter(lambda g: g.name == u.role, goals))[0].childs.append(newRef)
		refinements.append(newRef)

	else:
		newGoal = Goal(goalId)
		goalId += 1
		newGoal.setRoot()
		newGoal.setMandatory()
		newGoal.name = u.role
		goals.append(newGoal)
		newRef = Refinement(refinementId)
		refinementId += 1
		newRef.parent = newGoal.id_
		newGoal.childs.append(newRef)
		newGoal = Goal(goalId)
		goalId += 1
		newGoal.setLeaf()
		newGoal.name = u.action
		goals.append(newGoal)
		newRef.childs.append(newGoal)
		refinements.append(newRef)

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
			smt += c.id_ + ' '
		smt += ')))\r\n'

for r in refinements:
	smt += '(assert (and (= ' + r.id_ + ' (and '
	for c in r.childs:
		smt += c.id_ + ' '
	smt += ')) (=> ' + r.id_ + ' ' + r.parent + ' )))\r\n'

for g in goals:
	if g.isLeaf:
		smt += '(assert-soft (not ' + g.id_ +' ) :id sat_tasks)\r\n'

smt += '(minimize unsat_requirements)\r\n(minimize sat_tasks)\r\n(check-sat)\r\n(get-objectives)\r\n(load-objective-model 1)\r\n(get-model)\r\n(exit)'

print(smt)