## Copyright 2015-2019 Ilgar Lunin, Pedro Cabrera

## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at

##     http://www.apache.org/licenses/LICENSE-2.0

## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

import os
import sys
import json
import threading
import time

from Qt.QtWidgets import *
from Qt import QtGui
from Qt import QtCore
from PyFlow import INITIALIZE
from PyFlow.Core.Common import *
from PyFlow.Core.GraphManager import GraphManager
from PyFlow.UI.Canvas.UINodeBase import getUINodeInstance
from PyFlow.UI.Utils.stylesheet import editableStyleSheet
import PyFlow.UI.resources


def run(filePath):
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("plastique"))
    app.setStyleSheet(editableStyleSheet().getStyleSheet())

    msg = QMessageBox()
    msg.setWindowIcon(QtGui.QIcon(":/LogoBpApp.png"))
    msg.setIcon(QMessageBox.Critical)

    if os.path.exists(filePath):
        with open(filePath, 'r') as f:
            data = json.load(f)

        # Window to display inputs
        prop = QDialog()
        prop.setLayout(QVBoxLayout())
        prop.setWindowTitle(filePath)
        prop.setWindowIcon(QtGui.QIcon(":/LogoBpApp.png"))

        # Initalize packages
        try:
            INITIALIZE()
            man = GraphManager()
            man.deserialize(data)
            grph = man.findRootGraph()
            inputs = grph.getNodesByClassName("graphInputs")

            # If no GraphInput Nodes Exit propgram
            if len(inputs) > 0:
                for inp in inputs:
                    uiNode = getUINodeInstance(inp)
                    uiNodeJsonTemplate = inp.serialize()
                    uiNodeJsonTemplate["wrapper"] = inp.wrapperJsonData
                    uiNode.postCreate(uiNodeJsonTemplate)
                    cat = uiNode.createOutputWidgets(prop.layout(), inp.name)
                    prop.show()

                # fake main loop
                stopEvent = threading.Event()

                def programLoop(stopEvent):
                    while not stopEvent.is_set():
                        man.Tick(deltaTime=0.02)
                        time.sleep(0.02)
                t = threading.Thread(target=programLoop, args=(stopEvent,))
                t.start()

                def quitEvent():
                    stopEvent.set()
                    t.join()
                app.aboutToQuit.connect(quitEvent)
            else:
                msg.setInformativeText(filePath)
                msg.setDetailedText("The file doesn't containt graphInputs nodes")
                msg.setWindowTitle("PyFlow Ui Graph Parser")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.show()

        except Exception as e:
            msg.setText("Error reading Graph")
            msg.setInformativeText(filePath)
            msg.setDetailedText(str(e))
            msg.setWindowTitle("PyFlow Ui Graph Parser")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.show()

    else:
        msg.setText("File Not Found")
        msg.setInformativeText(filePath)
        msg.setWindowTitle("PyFlow Ui Graph Parser")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.show()

    try:
        sys.exit(app.exec_())
    except Exception as e:
        print(e)
