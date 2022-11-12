import sys
import traceback

from PyQt5 import QtCore

import Interface

if QtCore.QT_VERSION >= 0x50501:
    def excepthook(type_, value, traceback_):
        traceback.print_exception(type_, value, traceback_)
        QtCore.qFatal('')


    sys.excepthook = excepthook

print("Started!")

Interface.GUI()

#GUI needs to have it's own thread to run correct. Thus, all of the operations needs to be carried out there.