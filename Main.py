import re

lines = []

f = open("us.txt", "r").read().splitlines()

for x in f:
	if x:
		lines.append(x)

actors = []
goals = []
reasons = []

for line in lines:
	line = re.sub("[^A-Za-z']+", ' ', str(line)).lower()
	result = re.search('as (a|an) (.*) i want to (.*) (so that i|so i|so that) (.*).', line)
	act_ = result.group(2).replace(" ", "_")
	goal_ = result.group(3).replace(" ", "_")
	reason_ = result.group(5).replace(" ", "_")
	actors.append(act_.replace("'", "_"))
	goals.append(goal_.replace("'", "_"))
	reasons.append(reason_.replace("'", "_"))

# actors = ['A', 'A', 'B']
# goals = ['C', 'D', 'E']

class Refinement:
	def __init__(self, name):
		self.name = name
		self.childs = []
		self.parent
	def addChild(self, child):
		self.childs.append(child)
	def setParent(self, parent):
		self.parent = parent

class Goal:
	def __init__(self, name):
		self.name = name
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
	def addChild(self, child):
		self.childs.append(child)

goals = []
refinements = []

smt = '(set-option :produce-models true)\r\n(set-option :opt.priority lex)\r\n\r\n'

for g in goals:
	smt += '(declare-fun ' + g.name + ' () Bool) \r\n'
	if g.isMandatory:
		smt += '(assert ' + g.name + ')\r\n(assert-soft ' + g.name +' :id unsat_requirements)\r\n'

for r in refinements:
	smt += '(declare-fun ' + r.name + ' () Bool) \r\n'

for g in goals:
	if not g.isLeaf:
		smt += '(assert (=> ' + g.name + '(or '
		for c in g.childs:
			smt += c + ' '
		smt += ')))\r\n'

for r in refinements:
	smt += '(assert (and (= ' + r.name + ' (and '
	for c in r.childs:
		smt += c + ' '
	smt += ')) (=> ' + r.name + ' ' + r.parent + ' )))\r\n'

for g in goals:
	if g.isLeaf:
		smt += '(assert-soft (not ' + g.name +' ) :id sat_tasks)\r\n'

smt += '(minimize unsat_requirements)\r\n(minimize sat_tasks)\r\n(check-sat)\r\n(get-objectives)\r\n(load-objective-model 1)\r\n(get-model)\r\n(exit)'

print(smt)