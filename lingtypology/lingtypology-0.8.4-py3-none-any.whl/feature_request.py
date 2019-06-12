languages = ['Icelandic', 'Lezgian', 'Swahili', 'English', 'South Azerbaijani', 'Latin', 'Russian', 'French', 'Portuguese', 'Spanish', 'German', 'Saami', 'Ancient Greek', 'Modern Greek', 'Uzbek', 'Eastern Armenian', 'Karaim', 'Tabasaran']

data = [[['Polysemy', 'umsnúa', 'to turn', 'umsnúa', 'to transform', 0]], [['Polysemy', 'elqːün', 'to spin, to swirl', 'elqːün', 'to turn into', 0]], [['Polysemy', 'pindua', 'to turn, to topple', 'pindua', 'to transform', 0]], [['Polysemy', 'awendan', 'to turn away/off, avert, remove, turn upside down', 'awendan', 'turn', 0], ['Polysemy', 'turn', '', 'turn', '', 0]], [['Polysemy', 'dön-', 'to turn (back), to roll over', 'dön-', 'to turn into', 0], ['Polysemy', 'çevir-', 'to turn', 'çevir-', 'to transform', 0]], [['Polysemy', 'verto', 'to spin', 'verto', 'to transform', 0], ['Cognates', 'verto', 'to turn', 'werden', 'to become', 2]], [['Polysemy', "obernut'sja", 'to turn', "obernut'sja", 'to turn into', 0], ['Derivation', "vraščat'sja", 'to spin, to rotate', "prevratit'sja", 'to turn into', 0]], [['Cognates', 'tourner', 'to spin', 'tornar-se', 'to turn into, to become', 1]], [['Cognates', 'tourner', 'to spin', 'tornar-se', 'to turn into, to become', 1]], [['Polysemy', 'volver', 'to turn', 'volver', 'to transform', 0]], [['Cognates', 'verto', 'to turn', 'werden', 'to become', 2]], [['Polysemy', 'коаввсэ', 'to turn (back)', 'коаввсэ', 'to become similar, to turn into', 0]], [['Semantic evolution', 'μετατρέπω', 'to turn back', 'μετατρέπω', 'to transform', 3]], [['Semantic evolution', 'μετατρέπω', 'to turn back', 'μετατρέπω', 'to transform', 3]], [['Polysemy', 'aylan-', 'to spin, to go round, to turn', 'aylan-', 'to turn into', 0]], [['Polysemy', 'dařnal', 'to turn (back)', 'dařnal', 'to turn into, to become', 0]], [['Polysemy', 'кайыр-', 'to turn, to rotate', 'кайыр-', 'to transform', 0]], [['Polysemy', 'ilt’i(b)k’ub', 'to spin, to roll', 'ilt’i(b)k’ub', 'to transform', 0]]] 

mg = [[d[0] for d in datum] for datum in data]
mg = [['Polysemy'], ['Polysemy'], ['Polysemy'], ['Polysemy', 'Polysemy'], ['Polysemy', 'Polysemy'], ['Polysemy', 'Cognates'], ['Polysemy', 'Derivation'], ['Cognates'], ['Cognates'], ['Polysemy'], ['Cognates'], ['Polysemy'], ['Semantic evolution'], ['Semantic evolution'], ['Polysemy'], ['Polysemy'], ['Polysemy'], ['Polysemy']]

m = LingMap(languages)
mapping =  {
    "Polysemy": "#0000FF",
    "Semantic evolution": "#008000",
    "Derivation": "#FF0000",
    "Cognates": "#FFFF00",
    "Borrowing": "#FFC0CB",
    "Grammaticalization": "#FF0000"
}
#m.popups = 
m.add_marker_groups(mg, mapping=mapping)
m.save('test.html')
