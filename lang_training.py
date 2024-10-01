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
        #phrase = phrase.replace(r'\n', '\n')
        matches = []
        for res in re.finditer('{(.+?)}', phrase):
            #print(f'DEBUG - res = {res}')
            matches.append([res.start(), res.end()])
        return matches
    #-------------------------------------------------------------------------
    def removeBraces(self, text):
        return text.replace('{', '').replace('}', '')
    #-------------------------------------------------------------------------
    def getDefinedQuery(self, phrase, fillers, index):
        #extract the filler
        start, end = fillers[index]
        answer = phrase[start + 1: end - 1]
        #replace the filler
        prePhrase  = self.removeBraces(phrase[:start]).strip()
        postPhrase = self.removeBraces(phrase[end:]).strip()
        if prePhrase.startswith('('):
            parClose = prePhrase.index(')')
            statement = prePhrase[1: parClose]
            prePhrase = prePhrase[parClose + 1:].strip()
        else:
            statement = ''
        statement = statement.replace(r'\n ', '\n')    
        statement = statement.replace(r'\n', '\n')
        return statement, prePhrase, [answer.lower()], postPhrase, None
    #-------------------------------------------------------------------------
    def getQuery(self):
        phrase = random.choice(self.phrases)
        fillers = self.getFillers(phrase)
        index = random.choice(range(len(fillers)))
        return self.getDefinedQuery(phrase, fillers, index)
#-------------------------------------------------------------------------
class queryGeneratorClass:
    #---------------------------------------------------------------------
    def __init__(self):
        self.sources = []
        self.weights = []
    #---------------------------------------------------------------------
    def addSource(self, source, weight):
        self.sources.append(source)
        self.weights.append(weight)
    #---------------------------------------------------------------------
    def getQuery(self):
        return random.choices(self.sources, weights = self.weights)[0].getQuery()
#-------------------------------------------------------------------------
if __name__ == '__main__':
    generator = queryGeneratorClass()
    #generator.addSource(regVerbesClass(),                                  1)
    #generator.addSource(templateQueryGeneratorClass('interrogatif.ltr'),   3)
    #generator.addSource(templateQueryGeneratorClass('famille.ltr'),        3)
    generator.addSource(templateQueryGeneratorClass('genres.ltr'),         3)
    hits = 0
    misses = 0
    statement, prePhrase, answers, postPhrase, hint = generator.getQuery()
    while True:
        print('----------------------------------------------------')
        print(f'statement  = "{statement}"')
        print(f'prePhrase  = "{prePhrase}"')
        print(f'answer     = "{answers[0]}"')
        print(f'postPhrase = "{postPhrase}"')
        print(f'hint       = "{hint}"')
        query = statement + '\n' + prePhrase + ' ' + QUERY_SPACE + ' ' + postPhrase
        print(query)
        cand = input()
        if True:#cand.strip().lower() in answers:
            print('Correct!')
            hits += 1
            statement, prePhrase, answers, postPhrase, hint = generator.getQuery()
        else: 
            print(r'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\')
            print(f'Faux. Le bon est "{answers[0]}"')
            misses += 1
            print('////////////////////////////////////////////////////')
        total = misses + hits
        print(f'{hits} correct sur {total}: ({(hits/total):.2%}) \n')




