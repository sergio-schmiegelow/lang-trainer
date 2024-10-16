
#https://github.com/bretttolbert/verbecc
import csv
import json
import random
import sys
from unidecode import unidecode
from verbecc import Conjugator
#-------------------------------------------------------------------------
class regVerbesClass:
    #---------------------------------------------------------------------
    def __init__(self):
        self.tenses = ['présent', 'passé-composé', 'futur-proxe']
        with open('verbs_translations.csv', 'rt') as f:
            reader = csv.DictReader(f)
            if sys.platform == 'win32':
                self.ptTransDict = {}
                for row in reader:
                    key   = row['french'].encode('ISO-8859-1', errors='ignore').decode('utf-8', errors='ignore')
                    value = row['portuguese'].encode('ISO-8859-1', errors='ignore').decode('utf-8', errors='ignore')
                    self.ptTransDict[key] = value
            else:
                self.ptTransDict = {row['french']:row['portuguese'] for row in reader}
        self.regularVerbsList = [self.convertChars(v) for v in self.ptTransDict.keys() if self.parseVerb(v)[2] in [1, 2]]
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
        statement =  f'verbe: {verb} (en:{self.getConjugations(verb)["english"]} | pt:{self.ptTransDict[verb]})\n'
        statement += f'personne: {person}\n'
        statement += f'temp: {tense}'
        prePhrase = ''
        postPhrase = random.choice(self.complements[tense])
        answer = conjugated
        hint = None
        return statement, prePhrase, [answer], postPhrase, hint
    #-------------------------------------------------------------------------
    def getQuery(self):
        verb   = random.choice(self.regularVerbsList)
        person = random.choice(list(self.peopleDict.keys()))
        tense  = random.choice(self.tenses)
        return self.createDefinedQuery(verb, person, tense)
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
    #rv.testTemplate(['manger', 'aimer', 'se brosser', "s'appeler"])
    #quit()
    for verb in rv.regularVerbsList:
        for person in rv.peopleDict.keys():
            print('-------------------------------------')
            statement, prePhrase, [answer], postPhrase, hint = rv.createDefinedQuery(verb, person,'présent')
            print(f'statement  = "{statement}"')
            print(f'prePhrase  = "{prePhrase}"')
            print(f'answer     = "{answer}"')
            print(f'postPhrase = "{postPhrase}"')
            print(f'hint       = "{hint}"')
            print(statement)
            print(prePhrase + '{' + answer + '} ' + postPhrase)
    
    

