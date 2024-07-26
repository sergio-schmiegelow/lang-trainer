
#https://github.com/bretttolbert/verbecc
import json
from verbecc import Conjugator
#-------------------------------------------------------------------------
class regVerbesClass:
    #---------------------------------------------------------------------
    def __init__(self):
        with open('verbes_reguliers.txt', 'rt') as f:
            lines = f.readlines()
        self.verbsList = [l.strip() for l in lines if len(l)>2]
        self.regularVerbsList = [v for v in self.verbsList if self.parseVerb(v)[2] in [1, 2]]
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
        self.cg = Conjugator(lang='fr')
    #--------------------------------------------------------------------        
    def getConjugations(self, verb):
        '''
        r = requests.get(f'http://verbe.cc/verbecc/conjugate/fr/{verb}')
        if r.status_code != 200:
            print('ERROR in REST API request')
            return None
        #if r.headers['content-type'] != 'application/json; charset=utf8':
        if r.encoding != 'utf-8':
            print('ERROR not utf-8')
            return None
        isPronominal, radical, group = self.parseVerb(verb)
        
        rj = r.json()
        '''
        conjugations = {}
        conjDict = self.cg.conjugate(verb)

        present = conjDict['moods']['indicatif']['présent']
        print(f'DEBUG - present = {present}')
        present = [self.separateConjugateVerb(p) for p in present]
        conjugations['présent'] = present
        return conjugations
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
    def buildPersonVerbe(self, verb, tense, person):
        isPronominal, radical, group = self.parseVerb(verb)
        print(f'DEBUG - radical = {radical}')
        startVowel =  radical.startswith(tuple(self.vowels))
        conjugations = self.getConjugations(verb)[tense]
        personIndex = self.peopleDict[person]
        conjugatedWithPerson = conjugations[personIndex]
        conjugated = self.separateConjugateVerb(conjugatedWithPerson)
        outString = person + ' '
        if isPronominal:
            if startVowel:
                outString += self.pronomsVowel[personIndex] + ' '
            else:
                outString += self.pronoms[personIndex] + ' '
        outString += conjugated
        return outString
#-------------------------------------------------------------------------
rv = regVerbesClass()
print(rv.buildPersonVerbe('manger', 'présent', 'je'))
quit()
rv.getConjugations('manger')
rv.getConjugations('aimer')
rv.getConjugations('se brosser')
rv.getConjugations("s'appeler")
