from aitools.core import naive_bayes

X = [
    ['hi', 'what', 'is', 'up'],
    ['do', 'want', 'some', 'coffee'],
    ['can', 'you', 'pass', 'me', 'a', 'paper', 'towel'],
    ['hello', 'world']
]

y = [
    'greetings',
    'help',
    'help',
    'greetings'
]

x = [
    ['hi', 'what', 'is', 'up'],
    ['hi', 'do', 'you', 'want', 'some', 'coffee']
]

nb = naive_bayes.NaiveBayes(X, y)
nb.build()
nb.predict(x)
