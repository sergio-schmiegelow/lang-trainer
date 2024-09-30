import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer
import random
import sys

from lang_training import templateQueryGeneratorClass,  queryGeneratorClass
from conjugation import regVerbesClass
#-------------------------------------------------------------------------
class mainApp(QWidget):
    #---------------------------------------------------------------------
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Formation en langue française")
        self.setGeometry(100, 100, 600, 100)
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.statementLabel = QLabel('statement')
        self.mainLayout.addWidget(self.statementLabel)

        self.queryLayout = QHBoxLayout()
        self.prePhraseLabel = QLabel('preAnswer')
        self.answerInput = QLineEdit('')
        self.answerInput.returnPressed.connect(self.validadeAnswer)
        self.postPhraseLabel = QLabel('postAnswer')
        self.validadeButton = QPushButton('Valider')
        self.validadeButton.clicked.connect(self.validadeAnswer)
        self.queryLayout.addWidget(self.prePhraseLabel)
        self.queryLayout.addWidget(self.answerInput)
        self.queryLayout.addWidget(self.postPhraseLabel)
        self.queryLayout.addWidget(self.validadeButton)
        self.mainLayout.addLayout(self.queryLayout)

        self.validationLayout = QVBoxLayout()
        self.validationLabel = QLabel('')
        self.validationLayout.addWidget(self.validationLabel)
        self.mainLayout.addLayout(self.validationLayout)

        self.scoreLayout = QVBoxLayout()
        self.hitsLabel   = QLabel('Succès: 0')
        self.missesLabel = QLabel('Erreurs: 0')
        self.percentageLabel = QLabel('')
        self.percentageLabel.setVisible(False)
        self.scoreLayout.addWidget(self.hitsLabel)
        self.scoreLayout.addWidget(self.missesLabel)
        self.scoreLayout.addWidget(self.percentageLabel)
        self.mainLayout.addLayout(self.scoreLayout)

        self.sourcesList = []
        self.addSource(regVerbesClass(),                                      'verbes réguliers',   1)
        self.addSource(templateQueryGeneratorClass('verbes_irreguliers.ltr'), 'verbes irréguliers', 1)
        self.addSource(templateQueryGeneratorClass('interrogatif.ltr'),       'interrogatifs',      1)
        self.addSource(templateQueryGeneratorClass('famille.ltr'),            'famille',            1)
        self.addSource(templateQueryGeneratorClass('genres.ltr'),             'genres',             1)
        self.addSource(templateQueryGeneratorClass('pays.ltr'),               'pays',               1)

        self.hits = 0
        self.misses = 0
        self.setQuery()
    #---------------------------------------------------------------------
    def setQuery(self):
        statement, prePhrase, self.answers, postPhrase, hint = self.getQuery()
        self.statementLabel.setText(statement)
        self.prePhraseLabel.setText(prePhrase)
        self.answerInput.setText('')
        self.postPhraseLabel.setText(postPhrase)
        self.validationLabel.setText('')
    #---------------------------------------------------------------------
    def validadeAnswer(self):
        typedAnswer = self.answerInput.text().strip()
        if typedAnswer in self.answers:
            self.reportHit()
            self.validationLabel.setText('Correct!')
            self.validationLabel.setStyleSheet("color: blue;")
            QTimer.singleShot(1000, self.setQuery)
        else:
            self.reportMiss()
            self.validationLabel.setText(f'Faux. Le bon est "{self.answers[0]}"')
            self.validationLabel.setStyleSheet("color: red;")
        percentage = round((self.hits / (self.hits + self.misses)) * 100 )
        self.percentageLabel.setText(f'{percentage}%')
        self.percentageLabel.setVisible(True)
    #---------------------------------------------------------------------
    def reportHit(self):
        self.hits += 1
        self.hitsLabel.setText(f'Succès: {self.hits}')
    #---------------------------------------------------------------------
    def reportMiss(self):
        self.misses += 1
        self.missesLabel.setText(f'Erreurs: {self.misses}')
    #---------------------------------------------------------------------
    def addSource(self, source, label, weight):
        sourceDict = {'source':source, 'label':label, 'weight':weight}
        self.sourcesList.append(sourceDict)
    #---------------------------------------------------------------------
    def getQuery(self):
        sourcesList = [i['source'] for i in self.sourcesList]
        weightsList = [i['weight'] for i in self.sourcesList]
        return random.choices(sourcesList, weights = weightsList)[0].getQuery()
#-------------------------------------------------------------------------
def main():
    app = QApplication(sys.argv)
    window = mainApp()
    window.show()
    sys.exit(app.exec_())
#-------------------------------------------------------------------------
if __name__ == "__main__":
    x='asd'
    
    main()