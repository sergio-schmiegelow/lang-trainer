import re
import sys
import random
from conjugation import regVerbesClass
QUERY_SPACE = '___'
#-------------------------------------------------------------------------
class templateQueryGeneratorClass:
    def __init__(self, filename):
        self.phrases = []
        with open(filename) as fp:
            lines = fp.readlines()
            for line in lines:
                line = line.strip()
                if len(line.strip()) > 0:
                    self.phrases.append(line.strip())
    #-------------------------------------------------------------------------
    def getFillers(self, phrase):
        matches = []
        for res in re.finditer('{(.+?)}', phrase):
            #print(f'DEBUG - res = {res}')
            matches.append([res.start(), res.end()])
        return matches
    #-------------------------------------------------------------------------
    def getDefinedQuery(self, phrase, fillers, index):
        #extract the filler
        start, end = fillers[index]
        answer = phrase[start + 1: end - 1]
        #replace the filler
        queryPhrase = phrase[:start] + QUERY_SPACE + phrase[end:]
        queryPhrase = queryPhrase.replace('{', '')
        queryPhrase = queryPhrase.replace('}', '')
        if queryPhrase.startswith('('):
            parClose = queryPhrase.index(')')
            query = queryPhrase[1: parClose] + '\n' + queryPhrase[parClose + 1:].strip()
        else:
            query = queryPhrase
        return query, [answer.lower()], ''
    #-------------------------------------------------------------------------
    def getQuery(self):
        phrase = random.choice(self.phrases)
        fillers = self.getFillers(phrase)
        index = random.choice(range(len(fillers)))
        return self.getDefinedQuery(phrase, fillers, index)
#-------------------------------------------------------------------------
generators = []
generators.append(regVerbesClass())
generators.append(templateQueryGeneratorClass('interrogatif.ltr'))
generators.append(templateQueryGeneratorClass('famille.ltr'))
generators.append(templateQueryGeneratorClass('genres.ltr'))
hits = 0
misses = 0
query, answers, hint = random.choice(generators).getQuery()
while True:
    print('----------------------------------------------------')
    print(query)
    cand = input()
    if cand.strip().lower() in answers:
        print('Correct!')
        hits += 1
        query, answers, hint = random.choice(generators).getQuery()
    else: 
        print(r'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\')
        print(f'Faux. Le bon est "{answers[0]}"')
        misses += 1
        print('////////////////////////////////////////////////////')
    total = misses + hits
    print(f'{hits} correct sur {total}: ({(hits/total):.2%}) \n')

quit()

phrases = []
for dataFilename in sys.argv[1:]:
    #print(f'DEBUG dataFilename = {dataFilename}')
    with open(dataFilename) as fp:
        lines = fp.readlines()
        for line in lines:
            line = line.strip()
            if len(line.strip()) > 0:
                phrases.append(line.strip())
random.shuffle(phrases)
hits = 0
misses = 0


queryPhrase, word = generateQuery(phrases)
while True:
    print('----------------------------------------------------')
    print(queryPhrase)
    cand = input()
    if cand.strip().lower() == word.lower():
        print('Correto!')
        hits += 1
        queryPhrase, word = generateQuery(phrases)
    else: 
        print(r'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\')
        print(f'Errado. o correto é "{word}"')
        misses += 1
        print('////////////////////////////////////////////////////')
    total = misses + hits
    print(f'{hits} acertos de {total}: ({(hits/total):.2%}) \n')



