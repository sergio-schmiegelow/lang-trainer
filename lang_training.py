import re
import sys
import random
QUERY_SPACE = '___'
#-------------------------------------------------------------------------
def getFillers(phrase):
    matches = []
    for res in re.finditer('{(.+?)}', phrase):
        #print(f'DEBUG - res = {res}')
        matches.append([res.start(), res.end()])
    return matches
#-------------------------------------------------------------------------
def getQuery(phrase, fillers, index):
    #extract the filler
    start, end = fillers[index]
    word = phrase[start + 1: end - 1]
    #replace the filler
    queryPhrase = phrase[:start] + QUERY_SPACE + phrase[end:]
    queryPhrase = queryPhrase.replace('{', '')
    queryPhrase = queryPhrase.replace('}', '')
    return queryPhrase, word
#-------------------------------------------------------------------------
phrases = []
for dataFilename in sys.argv[1:]:
    #print(f'DEBUG dataFilename = {dataFilename}')
    with open(dataFilename) as fp:
        lines = fp.readlines()
        for line in lines:
            line = line.strip()
            if len(line.strip()) > 0:
                phrases.append(line.strip())
'''
for phrase in phrases:
    print(f'DEBUG - phrase = {phrase}')
    fillers = getFillers(phrase)
    print(f'DEBUG - fillers = {fillers}')
    queryPhrase, word  = getQuery(phrase, fillers, 0)
    print(f'DEBUG - queryPhrase = "{queryPhrase}", word = "{word}"')
'''
phrase = random.choice(phrases)
while True:
    fillers = getFillers(phrase)
    #rint(f'DEBUG - fillers = {fillers}')
    index = random.choice(range(len(fillers)))
    queryPhrase, word  = getQuery(phrase, fillers, index)
    #print(f'DEBUG - queryPhrase = "{queryPhrase}", word = "{word}"')
    print(queryPhrase)
    cand = input()
    if cand.strip() == word:
        print('Correto!')
        phrase = random.choice(phrases)
    else: 
        print(f'Errado. o correto é "{word}"')




