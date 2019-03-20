class Node:
	def __init__(self, name, ands, ors, parent):
		self.name = name
		self.ands = ands
		self.ors = ors
		self.isRoot = False
		self.parent = parent

	def __setRoot__(self):
		self.isRoot = True

smt = '(set-option :produce-models true)\r\n'

D = Node('D',[],[],'R2')
E = Node('E',[],[],'R3')
R2 = Node('R2',[D],[],'C')
R3 = Node('R3',[E],[],'C')
C = Node('C',[],[R2, R3],'R1')
B = Node('B',[],[],'R1')
F = Node('F',[],[],'R1')
R1 = Node('R1',[B,C,F],[],'A')
A = Node('A',[],[R1],None)
A.__setRoot__()

nodes = [C,D,R1,B,A,E,F,R2,R3]

for n in nodes:
	smt += '(declare-fun ' + n.name + ' () Bool) \r\n'
	if n.isRoot:
		smt += '(assert ' + n.name + ') \r\n'



for n in nodes:
	if  n.ands:
		smt += '(assert (and (= ' + n.name + ' (and '
		for a in n.ands:
			smt += a.name + ' '
		smt += ')) (=> ' + n.name + ' ' + n.parent + ' )))\r\n'

	if n.ors:
		smt += '(assert (=> ' + n.name + '(or '
		for o in n.ors:
			smt += o.name + ' '
		smt += ')))\r\n'

print(smt)