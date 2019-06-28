from random import randrange;

strings = \
[
"Nolite te bastardes corborundorum.",
"Whatever you do like to do, take it seriously.",
"Waiting for the sky to fall will cause more bother than sky actually falling.",
"Persistency is the word of the day.",
"The most important thing to do if you find yourself in a hole is to stop digging.",
"Suffering ceazes to be suffering at the moment it fnds meaning.",
"Anger is the ultimate destroyer of your own peace of mind.",
"Only one thing is ever guaranteed, that is that you will definitely not achieve the goal if you don't take the shot."
];

def randomString():

    random_index = randrange(len(strings));

    return strings[random_index];