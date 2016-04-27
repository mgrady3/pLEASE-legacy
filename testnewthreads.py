import sys
from newthreads import Worker
from PyQt4 import QtCore, QtGui


def TEST_usingMoveToThread():
    app = QtCore.QCoreApplication([])
    objThread = QtCore.QThread()
    obj = Worker(task='LOAD_LEEM')
    obj.moveToThread(objThread)
    obj.finished.connect(objThread.quit)
    objThread.started.connect(obj.work_to_do)
    objThread.finished.connect(app.exit)
    objThread.start()
    sys.exit(app.exec_())

if __name__ == '__main__':
    TEST_usingMoveToThread()