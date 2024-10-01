import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import *
import random
import sys

from lang_training import templateQueryGeneratorClass,  queryGeneratorClass
from conjugation import regVerbesClass
CONFIG_FILENAME = 'config.json'
#-------------------------------------------------------------------------
class mainApp(QWidget):
    #---------------------------------------------------------------------
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Formation en langue française")
        self.setGeometry(100, 100, 600, 100)
        self.setFixedHeight(250)
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)

        self.restartButtonLayout = QHBoxLayout()
        self.restartButton = QPushButton('Redémarrer')
        self.restartButton.clicked.connect(self.onRestart)
        self.restartButtonLayout.addWidget(self.restartButton)
        self.restartButtonLayout.addStretch()
        self.mainLayout.addLayout(self.restartButtonLayout)

        self.statementLayout = QVBoxLayout()
        self.statementLabel = QLabel('statement')
        self.statementLayout.addChildWidget(self.statementLabel)
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
        self.hitsLabel   = QLabel('')
        self.missesLabel = QLabel('')
        self.percentageLabel = QLabel('Paramètres')
        self.percentageLabel.setVisible(False)
        self.scoreLayout.addWidget(self.hitsLabel)
        self.scoreLayout.addWidget(self.missesLabel)
        self.scoreLayout.addWidget(self.percentageLabel)
        self.mainLayout.addLayout(self.scoreLayout)

        self.configButtonLayout = QHBoxLayout()
        self.configButton = QPushButton('Configuration')
        self.configButton.clicked.connect(self.onConfigButton)
        self.configButton.setCheckable(True)
        self.configButton.setChecked(False)
        self.configButtonLayout.addWidget(self.configButton)
        self.configButtonLayout.addStretch()
        self.mainLayout.addLayout(self.configButtonLayout)

        self.configWidget = QWidget() #To hide the layout
        self.configWidget.setVisible(False) 
        self.configLayout = QHBoxLayout(self.configWidget)
        self.sourcesList = []
        self.addSource(regVerbesClass(),                                      'verbes réguliers')
        self.addSource(templateQueryGeneratorClass('verbes_irreguliers.ltr'), 'verbes irréguliers')
        self.addSource(templateQueryGeneratorClass('interrogatif.ltr'),       'interrogatifs')
        self.addSource(templateQueryGeneratorClass('famille.ltr'),            'famille')
        self.addSource(templateQueryGeneratorClass('genres.ltr'),             'genres')
        self.addSource(templateQueryGeneratorClass('pays.ltr'),               'pays')
        self.mainLayout.addWidget(self.configWidget)
        self.createSourcesGrid()

        self.onRestart()
    #---------------------------------------------------------------------
    def onRestart(self):
        self.hits = 0
        self.misses = 0
        self.setQuery()
        self.hitsLabel.setText('Succès: 0')
        self.missesLabel.setText('Erreurs: 0')
        self.percentageLabel.setVisible(False)
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
        typedAnswer = self.answerInput.text().strip().lower()
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
    def addSource(self, source, label):
        sourceDict = {'source':source, 'label':label}
        self.sourcesList.append(sourceDict)
    #---------------------------------------------------------------------
    def getQuery(self):
        sourcesList = [i['source'] for i in self.sourcesList]
        labelsList  = [i['label']  for i in self.sourcesList]
        weightsList = [self.configDict['weights'][label] for label in labelsList]
        return random.choices(sourcesList, weights = weightsList)[0].getQuery()
    #---------------------------------------------------------------------
    def createSourcesGrid(self):
        with open(CONFIG_FILENAME, 'rt') as f:
            self.configDict = json.load(f)
        self.sourcesGrid = QGridLayout()
        self.sourcesGrid.addWidget(QLabel('Thème'), 0, 0, alignment = Qt.AlignLeft)
        self.sourcesGrid.addWidget(QLabel('Poids'), 0, 1)
        for idx, sourceDict in enumerate(self.sourcesList):
            sourceDict['sourceLabel'] = QLabel(sourceDict['label'])
            sourceDict['weightSelector'] = QSpinBox()
            sourceDict['weightSelector'].setRange(0, 99)
            sourceDict['weightSelector'].setValue(self.configDict['weights'][sourceDict['label']])
            sourceDict['weightSelector'].valueChanged.connect(self.onConfigChanged)
            self.sourcesGrid.addWidget(sourceDict['sourceLabel'],    idx + 1, 0, alignment = Qt.AlignLeft)
            self.sourcesGrid.addWidget(sourceDict['weightSelector'], idx + 1, 1, alignment = Qt.AlignRight)
        self.configLayout.addLayout(self.sourcesGrid)
        self.configLayout.addStretch()
        self.onConfigChanged()
    #---------------------------------------------------------------------
    def onConfigButton(self):
        with open(CONFIG_FILENAME, 'rt') as f:
            self.configDict = json.load(f)
        if self.configButton.isChecked():
            self.configWidget.setVisible(True)
            self.configButton.setText('Fermer la configuration')
            self.setFixedHeight(450)
        else:
            self.configWidget.setVisible(False)
            self.configButton.setText('Configuration')
            self.setFixedHeight(250)
    #---------------------------------------------------------------------
    def saveConfig(self):
        with open(CONFIG_FILENAME, 'wt') as f:
            f.write(json.dumps(self.configDict, indent = 4))
    #---------------------------------------------------------------------
    def onConfigChanged(self):
        for rowIdx in range(1, self.sourcesGrid.rowCount()):
            #print(f'DEBUG - rowIdx = {rowIdx}')
            labelWidget = self.sourcesGrid.itemAtPosition(rowIdx, 0).widget()
            label = labelWidget.text()
            value = int(self.sourcesGrid.itemAtPosition(rowIdx, 1).widget().text())
            if value == 0:
                labelWidget.setStyleSheet("color: gray")
            else:
                labelWidget.setStyleSheet("color: black")
            #print(f'label = {label}')
            #print(f'value = {value}')
            #print(f'type(value) = {type(value)}')
            self.configDict['weights'][label] = value
        self.saveConfig()
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