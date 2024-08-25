
#https://github.com/bretttolbert/verbecc
import csv
import json
import random
from unidecode import unidecode
from verbecc import Conjugator
#-------------------------------------------------------------------------
class regVerbesClass:
    #---------------------------------------------------------------------
    def __init__(self):
        self.tenses = ['présent', 'passé-composé', 'futur-proxe']
        with open('verbs_translations.csv', 'rt') as f:
            reader = csv.DictReader(f)
            ptTransDict = {row['french']:row['portuguese'] for row in reader}
        self.regularVerbsList = [self.convertChars(v) for v in ptTransDict.keys() if self.parseVerb(v)[2] in [1, 2]]
        self.peopleDict = {'je':0, 
                           'tu':1, 
                           'il':2,
                           'elle':2,
                           'on':2,
                           'nous':3,
                           'vous':4,
                           'ils':5,
                           'elles':5}
        self.basePeople      = ['je', 'tu', 'il', 'nous', 'vous', 'ils']
        self.people          = ['je', 'tu', 'il', 'elle', 'on', 'nous', 'vous', 'ils', 'elles']
                            
        self.pronoms =      ['me ', 'te ', 'se ', 'nous ', 'vous ', 'se ']
        self.pronomsVowel = ["m'", "t'", "s'", "nous ", "vous ", "s'"]
        self.vowels = ['a', 'e', 'i', 'o', 'u']
        self.passeComposePeople = ["j'ai", 'tu as', 'il a', 'elle a', 'on a', 'nous avons', 'vous avez', 'ils ont', 'elles ont']
        self.complements = {'présent':["aujourd'hui", "maintenant"],
                            'passé-composé':['hier', 'la semaine dernière', 'le mois dernier', "l'année dernière"],
                            'futur-proxe':['demain', 'après-demain', 'la semaine prochaine', 'le mois prochain', "l'année prochaine"]}
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
        conjugations['futur-proxe'] = []
        isPronominal, radical, group = self.parseVerb(infinitive)
        for presConj, fpPreffix in zip(conjugations['présent'], ['je vais ', 'tu vas ','il va ', 'nous allon ', 'vous allez ', 'ils vont ']):
            if isPronominal:
                person, pronoum, baseVerb = self.separatePronominalConjugated(presConj)
                #print(f'DEBUG - fpPreffix  = {fpPreffix}, pronoum {pronoum}, infinitive =  {infinitive}')
                conjugations['futur-proxe'].append(fpPreffix + pronoum + self.removePronominalInfinitive(infinitive))
            else:
                conjugations['futur-proxe'].append(fpPreffix + infinitive)
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
    def separatePronominalConjugated(self, conjugated):
        '''Valid only for indicatif - présent'''
        fields = conjugated.split(' ')
        if len(fields) == 2: #initiated in vowel
            return fields[0], fields[1][:2], fields[1][2:]
        return fields[0], fields[1] + ' ', fields[2:]
    #--------------------------------------------------------------------
    def removePronominalInfinitive(self, infinitive):
        '''Valid only for infitive'''
        if infinitive.startswith("s'"):
            return infinitive[2:]
        return infinitive.split(' ')[1] 
    #--------------------------------------------------------------------
    def getDefinedConjugation(self, verb, tense, person):
        conjugations = self.getConjugations(verb)
        conjTense = conjugations[tense]
        conjugationIndex = self.peopleDict[person]
        conjugated = conjTense[conjugationIndex]
        if person in ['elle', 'on', 'elles']:
            conjugated = person + ' ' + ' '.join(conjugated.split(' ')[1:])
        return conjugated
    #--------------------------------------------------------------------
    def createDefinedQuery(self, verb, person, tense):
        conjugated = self.getDefinedConjugation( verb, tense, person)
        query =  f'verbe: {verb} ({self.getConjugations(verb)["english"]})\n'
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
    def generateTestTemplate(self, verbs):
        testDict = {}  
        for verb in verbs:
            testDict[verb] = {}
            for tense in self.tenses:
                testDict[verb][tense] = {}
                for person in self.people:
                    conjugated = self.getDefinedConjugation(verb, tense, person)
                    testDict[verb][tense][person.strip()] = conjugated
        return testDict
    #-------------------------------------------------------------------------
    def testTemplate(self, verbs):
        with open('verbs_test_file.json', 'r') as f:
            refDict = json.load(f)
        testDict = self.generateTestTemplate(verbs)
        for verb in verbs:
            for tense in self.tenses:
                for person in self.people:
                    test = testDict[verb][tense][person]
                    ref  =  refDict[verb][tense][person]
                    #print(f'DEBUG - ref = {ref}, test = {test}')
                    if test != ref:
                        print(f'ERROR: verb: {verb}, tense: {tense}, person: {person}')
                        print(f'Should be "{ref}" but was "{test}"')
                        quit()
#-------------------------------------------------------------------------
if __name__ == '__main__':
    rv = regVerbesClass()
    rv.testTemplate(['manger', 'aimer', 'se brosser', "s'appeler"])
    quit()
    for verb in rv. regularVerbsList:
        for person in rv.peopleDict.keys():
            print('-------------------------------------')
            query, answer = rv.createDefinedQuery(verb, person,'présent')
            print(query)
            print(answer)
    #with open('verbs_test_file.json', 'wt') as f:
    #        json.dump(testDict, f, ensure_ascii=False, indent = 2)
    

