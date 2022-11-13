import traceback
from functools import partial
import sys, psycopg2

from PyQt5 import QtWidgets, QtSvg, QtCore, QtGui
from PyQt5.QtWidgets import QPushButton, QApplication, QVBoxLayout, QGroupBox, QTextEdit, QWidget, QTableWidget, QTableWidgetItem
from PyQt5.QtWebEngineWidgets import QWebEngineView


from blockdiag import parser, builder, drawer
from annotation import *
from preprocessing import *


SQL_QUERIES = [
    ["Select * from orders, customer where c_custkey = o_custkey and c_name = 'Cheng' ORDER BY c_phone"],
    [
        "Select l_returnflag,l_linestatus,sum(l_quantity) as sum_qty,sum(l_extendedprice) as sum_base_price,sum(l_extendedprice * (1-l_discount)) as sum_disc_price,sum(l_extendedprice * (1-l_discount) * (1+l_tax)) as sum_charge,avg(l_quantity) as avg_qty,avg(l_extendedprice) as avg_price,avg(l_discount) as avg_disc,count(*) as count_order from lineitem group by l_returnflag, l_linestatus order by l_returnflag, l_linestatus"]
]


class UI_MainWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1038, 592)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(10, 10, 511, 211))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.formLayoutWidget = QtWidgets.QWidget(self.groupBox)
        self.formLayoutWidget.setGeometry(QtCore.QRect(10, 20, 491, 149))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.formLayout.setLabelAlignment(QtCore.Qt.AlignCenter)
        self.formLayout.setFormAlignment(QtCore.Qt.AlignCenter)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setSpacing(1)
        self.formLayout.setObjectName("formLayout")
        self.label_7 = QtWidgets.QLabel(self.formLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_7)
        self.ip_address = QtWidgets.QLineEdit(self.formLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.ip_address.setFont(font)
        self.ip_address.setObjectName("ip_address")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.ip_address)
        self.label_6 = QtWidgets.QLabel(self.formLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_6)
        self.port_address = QtWidgets.QSpinBox(self.formLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.port_address.setFont(font)
        self.port_address.setMaximum(100000)
        self.port_address.setProperty("value", 5432)
        self.port_address.setObjectName("port_address")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.port_address)
        self.label = QtWidgets.QLabel(self.formLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label)
        self.username = QtWidgets.QLineEdit(self.formLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.username.setFont(font)
        self.username.setObjectName("username")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.username)
        self.label_3 = QtWidgets.QLabel(self.formLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.password = QtWidgets.QLineEdit(self.formLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.password.setFont(font)
        self.password.setObjectName("password")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.password)
        self.label_4 = QtWidgets.QLabel(self.formLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.db_n = QtWidgets.QLineEdit(self.formLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.db_n.setFont(font)
        self.db_n.setObjectName("db_n")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.db_n)
        self.label_8 = QtWidgets.QLabel(self.formLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_8.setFont(font)
        self.label_8.setAlignment(QtCore.Qt.AlignCenter)
        self.label_8.setObjectName("label_8")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.label_8)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.status_d = QtWidgets.QLabel(self.formLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.status_d.setFont(font)
        self.status_d.setTextFormat(QtCore.Qt.RichText)
        self.status_d.setAlignment(QtCore.Qt.AlignCenter)
        self.status_d.setObjectName("status_d")
        self.horizontalLayout.addWidget(self.status_d)
        self.formLayout.setLayout(6, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout)
        spacerItem = QtWidgets.QSpacerItem(0, 3, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.formLayout.setItem(5, QtWidgets.QFormLayout.LabelRole, spacerItem)
        self.connection_to_db = QtWidgets.QPushButton(self.groupBox)
        self.connection_to_db.setGeometry(QtCore.QRect(10, 170, 491, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.connection_to_db.setFont(font)
        self.connection_to_db.setObjectName("connection_to_db")
        self.layoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(0, 0, 2, 2))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setGeometry(QtCore.QRect(10, 220, 511, 351))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.groupBox_2.setFont(font)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.groupBox_2)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 20, 511, 331))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 4)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(10, 5, 10, 5)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.qList = QtWidgets.QComboBox(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.qList.sizePolicy().hasHeightForWidth())
        self.qList.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.qList.setFont(font)
        self.qList.setObjectName("qList")
        self.horizontalLayout_2.addWidget(self.qList)
        self.ldQ = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.ldQ.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ldQ.sizePolicy().hasHeightForWidth())
        self.ldQ.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.ldQ.setFont(font)
        self.ldQ.setObjectName("ldQ")
        self.horizontalLayout_2.addWidget(self.ldQ)
        self.horizontalLayout_2.setStretch(0, 2)
        self.horizontalLayout_2.setStretch(1, 7)
        self.horizontalLayout_2.setStretch(2, 2)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setContentsMargins(10, -1, 10, -1)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.txt_sql = QtWidgets.QTextEdit(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.txt_sql.setFont(font)
        self.txt_sql.setDocumentTitle("")
        self.txt_sql.setObjectName("txt_sql")
        self.verticalLayout_3.addWidget(self.txt_sql)
        self.verticalLayout.addLayout(self.verticalLayout_3)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.sql_btn = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.sql_btn.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sql_btn.sizePolicy().hasHeightForWidth())
        self.sql_btn.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.sql_btn.setFont(font)
        self.sql_btn.setObjectName("sql_btn")
        self.horizontalLayout_3.addWidget(self.sql_btn)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.horizontalLayout_3.setStretch(0, 1)
        self.horizontalLayout_3.setStretch(1, 8)
        self.horizontalLayout_3.setStretch(2, 1)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 8)
        self.verticalLayout.setStretch(2, 1)
        self.groupBox_3 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_3.setGeometry(QtCore.QRect(530, 12, 501, 559))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.groupBox_3.setFont(font)
        self.groupBox_3.setObjectName("groupBox_3")
        self.tW = QtWidgets.QTabWidget(self.groupBox_3)
        self.tW.setGeometry(QtCore.QRect(10, 20, 481, 531))
        self.tW.setMovable(False)
        self.tW.setObjectName("tW")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tW.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.connection_to_db.clicked.connect(self.ConnectSQL)
        self.sql_btn.clicked.connect(self.ExeSQLComm)
        self.ldQ.clicked.connect(self.displayQuery)

        ##HANDLE DISPLAYING TABLE
        # self.sql_btn.clicked.connect(self.DisplayTable)
        # self.tW.tabBarClicked.connect(self.DisplayTable)

        self.SQL_Connection = 123

        self.LoadQueriesToUI(SQL_QUERIES)

        self.CleanUI()

        QApplication.processEvents()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "CZ4031"))
        self.groupBox.setTitle(_translate("MainWindow", "SQL Connection"))
        self.label_7.setText(_translate("MainWindow", "Ip Address:"))
        self.ip_address.setText(_translate("MainWindow", "localhost"))
        self.label_6.setText(_translate("MainWindow", "Port:"))
        self.label.setText(_translate("MainWindow", "Username:"))
        self.username.setText(_translate("MainWindow", "postgres"))
        self.label_3.setText(_translate("MainWindow", "Password:"))
        self.password.setText(_translate("MainWindow", "admin"))
        self.label_4.setText(_translate("MainWindow", "Database Name:"))
        self.db_n.setText(_translate("MainWindow", "TPC-H"))
        self.label_8.setText(_translate("MainWindow", "Connection Status:"))
        self.status_d.setText(_translate("MainWindow",
                                         "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                         "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                         "p, li { white-space: pre-wrap; }\n"
                                         "</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
                                         "<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600; color:#ff0004;\">-Disconnected-</span></p></body></html>"))
        self.connection_to_db.setText(_translate("MainWindow", "Connect to postgreSQL"))
        self.groupBox_2.setTitle(_translate("MainWindow", "SQL Query"))
        self.label_2.setText(_translate("MainWindow", " Select Query:"))
        self.ldQ.setText(_translate("MainWindow", "Load Query"))
        self.txt_sql.setHtml(_translate("MainWindow",
                                        "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                        "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                        "p, li { white-space: pre-wrap; }\n"
                                        "</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
                                        "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.txt_sql.setPlaceholderText(_translate("MainWindow", "Type query command here, or load example query....."))
        self.sql_btn.setText(_translate("MainWindow", "Execute SQL Query"))
        self.groupBox_3.setTitle(_translate("MainWindow", "Annotations"))

    # Helper methods
    def CleanUI(self):
        for x in range(0, self.tW.count()):
            self.tW.removeTab(x)

    def displayQuery(self):
        self.txt_sql.setText(str(self.qList.itemData(self.qList.currentIndex()))[2:-2])

    def ConnectSQL(self):

        try:

            self.SQL_Connection = psycopg2.connect(
                host=self.ip_address.text(),
                database=self.db_n.text(),
                user=self.username.text(),
                password=self.password.text(),
                port=self.port_address.text())

            self.status_d.setStyleSheet("color: green; font-weight: 600")
            self.status_d.setText("Connected!")
            self.sql_btn.setEnabled(True)
            self.ldQ.setEnabled(True)

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    def LoadQueriesToUI(self, _qList):

        counter = 0
        for query in _qList:
            self.qList.addItem("Example Query No. " + str(counter), query)
            counter += 1

    def AddToTab(self, tab, obj):
        tab.layout.addWidget(obj)

    def ConnectToPostgreSQL(self):
        self.SQL_Connection = psycopg2.connect(
            host=self.ip_address.text(),
            database=self.db_n.text(),
            user=self.username.text(),
            password=self.password.text(),
            port=self.port_address.text())

    def TerminateConnectionToPostgreSQL(self):
        self.SQL_Connection.close()

    # Display diagram button
    def displayDiag(self, number):

        inner = ""
        for i in self.block_diag_relations[number]:
            inner = inner + i + '\n'

        diag_string = "blockdiag {orientation = portrait;\n" + inner + "}"


        tree = parser.parse_string(diag_string)

        diagram = builder.ScreenNodeBuilder.build(tree)

        draw = drawer.DiagramDraw('SVG', diagram)
        draw.draw()
        data = (draw.save())

        self.webView = QWebEngineView()

        self.webView.setHtml(data)

        svg_bytes = bytearray(data, encoding='utf-8')

        renderer = QtSvg.QSvgRenderer(svg_bytes)

        self.webView.resize(renderer.viewBox().size())

        self.webView.show()

    # ========= Main Function =========
    def ExeSQLComm(self):
        try:

            print("Start Query Execution process. It might take a lot of time! Application may freeze!")

            self.CleanUI()

            self.tW.removeTab(0)  # Need it?

            self.ConnectToPostgreSQL()

            self.c_r = self.SQL_Connection.cursor()

            QueryFromGUI = self.txt_sql.toPlainText()


            self.node_types_d = {}
            self.query_plans = {}
            #

            block_diag_relations = []
            # Formats query

            # Getting query plan
            node_types, res, self.query_plans = fetch_QEP(self.c_r, QueryFromGUI, self.query_plans, self.node_types_d)

            block_diag_relations.append(res)
            # fetching AQPS

            self.query_plans, self.block_diag_relations = fetch_AQPS(self.c_r, node_types, QueryFromGUI,
                                                                     self.query_plans, block_diag_relations)

            loop_v = 0
            for x in range(1, len(list(self.query_plans.values())[1:]) + 1):

                tab1 = QtWidgets.QWidget()
                tab1.layout = QVBoxLayout()
                groupbox = QGroupBox("Annotation")
                groupbox.setObjectName = "Annotation"
                vbox = QVBoxLayout()
                groupbox.setLayout(vbox)
                TEXT = QTextEdit()
                TEXT.setReadOnly(True)

                aqplist = list(self.query_plans.values())

                # Obtaining annotations
                test = traverse_qep(self.query_plans['0'], [aqplist[x]], "")
                test = test + compare_plans(self.query_plans['0'], aqplist[x])
                print(test)

                TEXT.setText(test)


                BUTTON2 = QPushButton("Display Mapping")

                BUTTON = QPushButton("Display Physical Query Plan")

                BUTTON.clicked.connect(partial(self.displayDiag, loop_v))
                BUTTON2.clicked.connect(self.DisplayTable)
                vbox.addWidget(TEXT)
                self.AddToTab(tab1, groupbox)
                self.AddToTab(tab1, BUTTON)
                self.AddToTab(tab1, BUTTON2)

                tab1.setLayout(tab1.layout)
                # tabs are being added also during 2nd execution of query
                if loop_v == 0:
                    self.tW.addTab(tab1, "QEP vs AQP1")
                else:
                    self.tW.addTab(tab1, "QEP vs AQP" + str(x))

                loop_v += 1


        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            self.TerminateConnectionToPostgreSQL()

    def DisplayTable(self):

        # Sample code to run the table window
        mapping = get_mapping(self.query_plans, self.txt_sql.toPlainText())

        self.data = {
            'Query Term': [],
            'QEP': []}

        AEP_counter = len(mapping)
        for i in range(AEP_counter - 1):
            self.data['AEP' + str(i + 1)] = []

        ammount_of_c = 0

        value = generate_table(mapping)

        for x in value:

            self.data["Query Term"].append(str(x[1]))

            if str(x[2]) == "None":
                self.data["QEP"].append("~")
            else:
                self.data["QEP"].append(str(x[2]))

            if "AEP1" in self.data:
                if str(x[3]) == "None":
                    self.data["AEP1"].append("~")
                else:
                    self.data["AEP1"].append(str(x[3]))

            if "AEP2" in self.data:
                if str(x[4]) == "None":
                    self.data["AEP2"].append("~")
                else:
                    self.data["AEP2"].append(str(x[4]))

            if "AEP3" in self.data:
                if str(x[5]) == "None":
                    self.data["AEP3"].append("~")
                else:
                    self.data["AEP3"].append(str(x[5]))

            if "AEP4" in self.data:
                if str(x[6]) == "None":
                    self.data["AEP4"].append("~")
                else:
                    self.data["AEP4"].append(str(x[6]))

            ammount_of_c += 1

        table = QTableWidget()

        table.setSizeAdjustPolicy(
            QtWidgets.QAbstractScrollArea.AdjustToContents)

        table.setColumnCount(len(self.data))
        table.setRowCount(ammount_of_c)  # Amount of data in each row

        horHeaders = []

        for n, key in enumerate((self.data.keys())):
            horHeaders.append(key)
            for m, item in enumerate(self.data[key]):
                newitem = QTableWidgetItem(item)

                table.setItem(m, n, newitem)
        table.setHorizontalHeaderLabels(horHeaders)


        self.main = QVBoxLayout()

        self.main.addWidget(table)

        table.resizeColumnsToContents()

        self.window = QWidget()

        self.window.setLayout(self.main)

        self.window.resize(self.main.sizeHint())

        self.window.show()


# Start GUI Threadz

def GUI():
    if QtCore.QT_VERSION >= 0x50501:
        def excepthook(type_, value, traceback_):
            traceback.print_exception(type_, value, traceback_)
            QtCore.qFatal('')

        sys.excepthook = excepthook

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = UI_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

