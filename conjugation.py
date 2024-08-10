
#https://github.com/bretttolbert/verbecc
import json
import random
from unidecode import unidecode
from verbecc import Conjugator
#-------------------------------------------------------------------------
class regVerbesClass:
    #---------------------------------------------------------------------
    def __init__(self):
        self.tenses = ['présent', 'passé-composé', 'futur-proxe']
        with open('verbes_reguliers.txt', 'rt') as f:
            lines = f.readlines()
        self.verbsList = [l.strip() for l in lines if len(l)>2]
        self.regularVerbsList = [self.convertChars(v) for v in self.verbsList if self.parseVerb(v)[2] in [1, 2]]
        self.peopleDict = {'je':0, 
                           'tu':1, 
                           'il':2,
                           'elle':2,
                           'on':2,
                           'nous':3,
                           'vous':4,
                           'ils':5,
                           'elles':5}
        
        self.people      = ['je ', 'tu ', 'il ', 'elle ', 'on ', 'nous ', 'vous ', 'ils ', 'elles ']
        self.peopleVowel = ["j'",  'tu ', 'il ', 'elle ', 'on ', 'nous ', 'vous ', 'ils ', 'elles ']
                            
        self.pronoms =      ['me ', 'te ', 'se ', 'nous ', 'vous ', 'se ']
        self.pronomsVowel = ["m'", "t'", "s'", "nous ", "vous ", "s'"]
        self.vowels = ['a', 'e', 'i', 'o', 'u']
        self.passeComposePeople = ["j'ai", 'tu as', 'il a', 'elle a', 'on a', 'nous avons', 'vous avez', 'ils ont', 'elles ont']
        self.complements = {'présent':["aujourd'hui", "maintenant"],
                            'passé-composé':['hier', 'la semaine dernière', 'le mois dernier', "l'année dernière"],
                            'futur-proxe':['demain', 'après-demain', 'la semaine prochaine', 'vais le mois prochain', "l'année prochaine"]}
        self.cg = Conjugator(lang='fr')
    #--------------------------------------------------------------------
    def convertChars(self, verb):
        return verb.replace('œ', 'oe')
    #--------------------------------------------------------------------        
    def getConjugations(self, verb):
        conjugations = {}
        try:
            conjDict = self.cg.conjugate(verb)
            #print(f'DEBUG - conjDict = {json.dumps(conjDict, indent = 2)}')
        except:
            return None
        conjugations['infinitive'] = verb
        conjugations['english'] = conjDict['verb']['translation_en']
        #print(f'DEBUG - conjDict = {json.dumps(conjDict, indent=2)}')
        for tense in ['présent', 'passé-composé']:
            conj = conjDict['moods']['indicatif'][tense]
            if len(conj) != 6:
               return None
            conjugations[tense] = conj
        self.generateFuturProxe(conjugations)
        #print(f'DEBUG - conjugations = {conjugations}')
        return conjugations
    #--------------------------------------------------------------------
    def generateFuturProxe(self, conjugations):
        infinitive = conjugations['infinitive']
        isPronominal, radical, group = self.parseVerb(infinitive)
        if isPronominal:
            conjugations['futur-proxe'] = ['je vais me '      + infinitive,
                                           'tu vas te '       + infinitive,
                                           'il va se '        + infinitive,
                                           'nous allon nous ' + infinitive,
                                           'vous allez vous ' + infinitive,
                                           'ils vont se'      + infinitive]
        else:
            conjugations['futur-proxe'] = ['je vais '    + infinitive,
                                           'tu vas '     + infinitive,
                                           'il va '      + infinitive,
                                           'nous allon ' + infinitive,
                                           'vous allez ' + infinitive,
                                           'ils vont '   + infinitive]
    #--------------------------------------------------------------------
    def parseVerb(self, verb):
        if verb.startswith("s'"):
            isPronominal = True
            radical = verb[2:-2]
            suffix = verb[-2:]
        elif verb.startswith("se "):
            isPronominal = True
            radical = verb[3:-2]
            suffix = verb[-2:]
        else:
            isPronominal = False
            radical = verb[:-2]
            suffix = verb[-2:]
        if suffix == 'er':
            group = 1
        elif suffix == 'ir':
            group = 2
        else:
            group = 3
            radical = None
        return isPronominal, radical, group
    #--------------------------------------------------------------------
    def separateConjugateVerb(self, conjugated):
        verb = conjugated.split(' ')[-1]
        if verb.startswith(("j'", "m'", "t'", "s'")):
            verb = verb[2:]
        return verb
    #--------------------------------------------------------------------
    def buildPersonVerb(self, verb, tense, person):
        isPronominal, radical, group = self.parseVerb(verb)
        startVowel =  unidecode(radical).startswith(tuple(self.vowels))
        conjugations = self.getConjugations(verb)[tense]
        if conjugations is None:
            return None
        personIndex = self.peopleDict[person]
        conjugatedWithPerson = conjugations[personIndex]
        conjugated = self.separateConjugateVerb(conjugatedWithPerson)
        if isPronominal:
            outString = person + ' '
            if startVowel:
                outString += self.pronomsVowel[personIndex]
            else:
                outString += self.pronoms[personIndex]
        else: #non pronominal
            if startVowel:
                outString = self.peopleVowel[self.people.index(person + ' ')]
            else:
                outString = person + ' '
        outString += conjugated
        return outString
    #--------------------------------------------------------------------
    def testVerb(self, verb):
        print(f'DEBUG - verb = {verb}')
        people = ['je', 'tu', 'il', 'nous', 'vous', 'ils']
        conjugations = self.getConjugations(verb)
        if conjugations is None:
            return None
        presentList = conjugations['présent']
        syntheticPresentList =[self.buildPersonVerb(verb, 'présent', person) for person in people]
        print(f'DEBUG - presentList          = {presentList}')
        print(f'DEBUG - syntheticPresentList = {syntheticPresentList}')
        if presentList == syntheticPresentList:
            print('Ok')
            return 0
        else:
            print('Fail')
            return 1
    #--------------------------------------------------------------------
    def testAllVerbs(self):
        matches = 0
        nonSupported = 0
        fails = 0
        for verb in self.regularVerbsList:
            res = self.testVerb(verb)
            if res is None:
                nonSupported += 1
                quit()
            elif res == 0:
                matches += 1
            else:
                fails += 1
                quit()
            print(f'matches = {matches}, fails = {fails}, nonSupported = {nonSupported}')
    #-------------------------------------------------------------------- 
    def createDefinedQuery(self, verb, person, tense):
        conjugations = self.getConjugations(verb)
        conjTense = conjugations[tense]
        conjugationIndex = self.peopleDict[person]
        conjugated = conjTense[conjugationIndex]
        if person in ['elle', 'on', 'elles']:
            conjugated = person + ' ' + ' '.join(conjugated.split(' ')[1:])
        query =  f'verbe: {verb} ({conjugations["english"]})\n'
        query += f'personne: {person}\n'
        query += f'temp: {tense}\n'
        query += f'___________ {random.choice(self.complements[tense])}'
        answer = conjugated
        return query, answer
    #-------------------------------------------------------------------------
    def getQuery(self):
        verb   = random.choice(self.regularVerbsList)
        person = random.choice(list(self.peopleDict.keys()))
        tense  = random.choice(self.tenses)
        query, answer = self.createDefinedQuery(verb, person, tense)
        hint = None
        return query, [answer], hint
#-------------------------------------------------------------------------
if __name__ == '__main__':
    rv = regVerbesClass()
    for verb in rv. regularVerbsList:
        for person in rv.peopleDict.keys():
            print('-------------------------------------')
            query, answer = rv.createDefinedQuery(verb, person,'présent')
            print(query)
            print(answer)
    

