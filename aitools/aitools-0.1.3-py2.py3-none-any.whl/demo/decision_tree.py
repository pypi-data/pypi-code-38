
from aitools.core import decision_tree

X = [
    ['Green', 3, 'Apple'],
    ['Yellow', 3, 'Apple'],
    ['Red', 1, 'Grape'],
    ['Red', 1, 'Grape'],
    ['Yellow', 3, 'Lemon'],
]

y = ['Sweet', 'Sweet', 'Sour', 'Sour', 'Better']

tree = decision_tree.DecisionTree(X, y)
tree.build()

#print(tree.predict(['Yellow', 3, 'Apple']))


