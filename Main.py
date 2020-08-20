from EX import card_reader
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon, QPixmap    #아이콘 관련 #이미지관련
import time

form_class = uic.loadUiType("C:/WorkSpace/python/card_reader/cardreader.ui")[0]


#메인창
class MyApp(QMainWindow, form_class):

    def information(self):
        msgbox = QMessageBox()
        msgbox.setWindowTitle('Information')
        msgbox.setText('만든이: 안영빈\n이메일: ayb8931@gmail.com\n버전: Test')
        msgbox.exec_()
    def timeout(self):
        self.statusBar().showMessage(time.strftime('%Y-%m-%d', time.localtime(time.time())))
    def fileOpen(self):
        info = QFileDialog.getOpenFileName(self, 'Open File', '', 'Image(*.png *jpg *.xpm)')
        if info == ('', ''):
            pass
        else:
            self.imagefile =info[0]
            self.textEdit.setText('사진을 선택하셨습니다\n카드 정보 읽기 버튼을 누르세요.')

    def Reset(self):
        self.textEdit.clear()
    def Help(self):
        self.textEdit.setText('1. "카드이미지 불러오기" 버튼을 눌러 카드 이미지 파일을 가지고 옵니다\n2. "카드 정보 읽기"버튼을 눌러 카드의 내용을 읽습니다.\nTip) 깔끔한 배경에 선명한 카드 사진일 수록  인식률이 올라갑니다! ')

    def read(self):
        im = self.cr.tesseracts(self.imagefile)
        try:
            if im == -1:
                self.textEdit.setText('------------------------------------\n                      warning\n------------------------------------\n사진을 읽지 못하였습니다.\n다른이미지를 넣어주세요.')
            elif im == -2:
                self.textEdit.setText('------------------------------------\n                      warning\n------------------------------------\n이미지를 먼저 넣어주세요.')
        except:
            text = self.cr.ocr_tesseract(im)
            index_result = self.cr.lookexcel(text)
            if index_result ==-1:
                self.textEdit.setText('------------------------------------\n                      warning\n------------------------------------\n카드번호를 못찾았습니다.\n다른이미지를 넣어주세요.')
            else:
                self.textEdit.setText(index_result)
    def __init__(self):

        super().__init__()
        self.setupUi(self)
        self.imagefile =None
        self.cr = card_reader.card_reader()

        # title
        self.setWindowTitle('Card Pin Reader')

        self.textEdit.setReadOnly(True)

        #OpenButton
        self.btn_Imageload.setToolTip('This is a <b>Image file read</b> Button')
        self.btn_Imageload.clicked.connect(self.fileOpen)

        #filereadbutton
        self.btn_ReadPin.setToolTip('This is a <b>get pin information</b> Button')
        self.btn_ReadPin.clicked.connect(self.read)

        #ExitButton
        self.btn_Exit.setToolTip('This is a <b>Exit Program</b> buttons')
        self.btn_Exit.clicked.connect(QCoreApplication.instance().quit)

        #상태바
        self.statusBar().showMessage(time.strftime('%Y-%m-%d', time.localtime(time.time())))
        self.timer = QTimer(self)
        self.timer.start(5000)
        self.timer.timeout.connect(self.timeout)

        #file메뉴 옵션
        exitAction = QAction('Exit', self)
        exitAction.setShortcut('Ctr+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)

        infoAction = QAction('information', self)
        infoAction.setShortcut('Ctr+i')
        infoAction.setStatusTip('application information')
        infoAction.triggered.connect(self.information)

        restartAction = QAction('ReStart', self)
        restartAction.setShortcut('Ctr+S')
        restartAction.setStatusTip('restart application')
        restartAction.triggered.connect(self.Reset)
        #menumenu 옵션
        openAction = QAction('Open', self)
        openAction.setShortcut('Ctr+O')
        openAction.setStatusTip('Open Image file')
        openAction.triggered.connect(self.fileOpen)

        readAction =  QAction('Read', self)
        readAction.setShortcut('Ctr+R')
        readAction.setStatusTip('Read Pin Number')
        readAction.triggered.connect(self.read)

        helpAction = QAction('Help',self)
        helpAction.setShortcut('Ctr+H')
        helpAction.setStatusTip('도움말')
        helpAction.triggered.connect(self.Help)
        #메뉴바
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)

        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(restartAction)
        fileMenu.addAction(infoAction)
        fileMenu.addAction(exitAction)

        MenuMenu = menubar.addMenu('&Menu')
        MenuMenu.addAction(openAction)
        MenuMenu.addAction(readAction)
        MenuMenu.addAction(helpAction)


        self.show()
if __name__ == '__main__':

    app = QApplication(sys.argv)
    myWindow = MyApp()
    # 프로그램 화면을 보여주는 코드
    myWindow.show();
    app.exec_()
