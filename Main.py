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
		self.pWeight = []
		self.nWeight = []
		self.content = None

a = UserStory(1)
b = UserStory(2)
c = UserStory(3)

a.role = 'publisher'
a.action = 'sign up'
a.pWeight.append(('pos', 3))
a.nWeight.append(('eff', 2))
b.role = 'publisher'
b.action = 'publish'
b.pWeight.append(('pos', 10))
b.nWeight.append(('eff', 1))
c.role = 'admin'
c.action = 'create profile'
c.pWeight.append(('pos', 4))
c.nWeight.append(('eff', 2))


userStories = []
goals = []
refinements = []

userStories.append(a)
userStories.append(b)
userStories.append(c)
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
		for p in u.pWeight:
			newGoal.pWeight.append(p)
		for n in u.nWeight:
			newGoal.nWeight.append(n)
		newGoal.name = u.action
		goals.append(newGoal)
		newRef = Refinement(refinementId)
		refinementId += 1
		newRef.children.append(newGoal)
		newRef.parent = list(filter(lambda g: g.name == u.role, goals))[0].id_
		list(filter(lambda g: g.name == u.role, goals))[0].children.append(newRef)
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
		newGoal.children.append(newRef)
		newGoal = Goal(goalId)
		goalId += 1
		newGoal.setLeaf()
		for p in u.pWeight:
			newGoal.pWeight.append(p)
		for n in u.nWeight:
			newGoal.nWeight.append(n)
		newGoal.name = u.action
		goals.append(newGoal)
		newRef.children.append(newGoal)
		refinements.append(newRef)

smt = '(set-option :produce-models true)\r\n(set-option :opt.priority lex)\r\n\r\n'

weightCount = 0

for g in goals:
	smt += '(declare-fun ' + g.id_ + ' () Bool) \r\n'
	if g.isMandatory:
		smt += '(assert ' + g.id_ + ')\r\n(assert-soft ' + g.id_ +' :id unsat_requirements)\r\n'

for r in refinements:
	smt += '(declare-fun ' + r.id_ + ' () Bool) \r\n'

for g in goals:
	if not g.isLeaf:
		smt += '(assert (=> ' + g.id_ + '(or '
		for c in g.children:
			smt += c.id_ + ' '
		smt += ')))\r\n'

for r in refinements:
	smt += '(assert (and (= ' + r.id_ + ' (and '
	for c in r.children:
		smt += c.id_ + ' '
	smt += ')) (=> ' + r.id_ + ' ' + r.parent + ' )))\r\n'

for g in goals:
	if g.isLeaf:
		smt += '(assert-soft (not ' + g.id_ +' ) :id sat_tasks)\r\n'
		for p in g.pWeight:
			smt += '(assert-soft (not ' + g.id_ +' ) :weight ' + str(p[1]) + ' :id ' + p[0] + ')\r\n'
		for n in g.nWeight:
			smt += '(assert-soft ' + g.id_ +' :weight ' + str(n[1]) + ' :id ' + n[0] + ')\r\n'

for p in userStories[0].pWeight:
	smt += '(minimize ' + p[0] + ')\r\n'
for n in userStories[0].nWeight:
	smt += '(minimize ' + n[0] + ')\r\n'

smt += '(minimize unsat_requirements)\r\n(minimize sat_tasks)\r\n(check-sat)\r\n(get-objectives)\r\n(load-objective-model 1)\r\n(get-model)\r\n(exit)'

print(smt)