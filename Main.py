import re

lines = []

f = open("story.txt", "r").read().splitlines()

for x in f:
	if x:
		lines.append(x)

actors = []
goals = []
reasons = []

for line in lines:
	result = re.search('As (a|an) (.*), I want to (.*), (So that I|so I|So that) (.*).', line)
	actors.append(result.group(2))
	goals.append(result.group(3))
	reasons.append(result.group(5))

print (actors)
print (goals)
print (reasons)