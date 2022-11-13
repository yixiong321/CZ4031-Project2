import traceback
from functools import partial

from PyQt5 import QtWidgets, uic, Qt, QtSvg, QtCore
import sys, psycopg2

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication, QVBoxLayout, QGroupBox, QTextEdit, QStyleFactory
from blockdiag import parser, builder, drawer

from annotation import *
from preprocessing import *
from PyQt5.QtWebEngineWidgets import QWebEngineView

SQL_QUERIES = [
    ["Select * from orders, customer where c_custkey = o_custkey and c_name = 'Cheng' ORDER BY c_phone"],
    ["Select l_returnflag,l_linestatus,sum(l_quantity) as sum_qty,sum(l_extendedprice) as sum_base_price,sum(l_extendedprice * (1-l_discount)) as sum_disc_price,sum(l_extendedprice * (1-l_discount) * (1+l_tax)) as sum_charge,avg(l_quantity) as avg_qty,avg(l_extendedprice) as avg_price,avg(l_discount) as avg_disc,count(*) as count_order from lineitem group by l_returnflag, l_linestatus order by l_returnflag, l_linestatus"]
]



class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        uic.loadUi("MainUI.ui", self)

        self.setWindowTitle("Project 2")

        #Connect buttons to code
        self.connection_to_db.clicked.connect(self.ConnectSQL)
        self.sql_btn.clicked.connect(self.ExeSQLComm)
        self.ldQ.clicked.connect(self.displayQuery)

        #self.dQp1.clicked.connect(self.displayDiag)

        self.SQL_Connection = 123

        self.LoadQueriesToUI(SQL_QUERIES)

        self.CleanUI()

        QApplication.processEvents()

        self.show()

    # Helper methods
    def CleanUI(self):
        for x in range(0, self.tW.count()):
            self.tW.removeTab(x)

    def displayQuery(self):
        self.txt_sql.setText(str(self.qList.itemData(self.qList.currentIndex()))[2:-2])

    def ConnectSQL(self):
        print("Clicked!")

        try:

            self.SQL_Connection = psycopg2.connect(
                host=self.ip_address.text(),
                database= self.db_n.text(),
                user= self.username.text(),
                password= self.password.text())

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
            password=self.password.text())

    def TerminateConnectionToPostgreSQL(self):
        self.SQL_Connection.close()

    #Display diagram button
    def displayDiag(self, number):
        inner =""
        for i in self.block_diag_relations[number]:
            inner=inner+i+'\n'
        #print(inner)
        diag_string = "blockdiag {orientation = portrait;\n" + inner + "}"

        print(diag_string)

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

    #========= Main Function =========
    def ExeSQLComm(self):
        try:

            self.CleanUI()

            self.tW.removeTab(0) #Need it?

            self.ConnectToPostgreSQL()

            self.c_r = self.SQL_Connection.cursor()

            QueryFromGUI = self.txt_sql.toPlainText()

            # self.c_r.execute("EXPLAIN (ANALYZE, VERBOSE, FORMAT JSON)" + QueryFromGUI)

            # records = self.c_r.fetchall()

            self.node_types_d = {}
            self.query_plans = {}
            #

            block_diag_relations = []
            # Formats query

            # Getting query plan
            node_types, res, self.query_plans = fetch_QEP(self.c_r, QueryFromGUI, self.query_plans, self.node_types_d)

            block_diag_relations.append(res)
            # fetching AQPS
            if len(node_types) > 1:
                self.query_plans, self.block_diag_relations = fetch_AQPS(self.c_r, node_types.keys(), QueryFromGUI,
                                                                         self.query_plans, block_diag_relations)
            # query_plans stores list of plans , [QEP, 'rest of AQPs']
            # aqp_relations stores list of string input for blockdiags for AQPs
        
            mapping = get_mapping(self.query_plans,QueryFromGUI)
            head = ['Line No.', 'Query Terms', 'QEP']
            AEP_counter = len(mapping)
            for i in range(AEP_counter):
                head.append('AEP' + str(i+1))
            
            print("in interface head is:")
            print(head)
            x = tabulate(generate_table(mapping), headers=head, tablefmt="grid")
            # for i in mapping:
            #     print()
            #     i.print_sql_query_list()

            # #This gets all the query terms of a query in a list
            # qtlist = mapping[0].return_query_terms_list()
            # nodelinelist = mapping[0].return_node_line()
            # print("SIZE OF QUERY TERMS LIST: " + str(len(qtlist)))
            # #print(tabulate(qtlist, tablefmt="grid"))
            # head = ["Line No.", "Query Term", "Annotation"]

            # table = [["" for i in range(3)] for j in range(len(qtlist))]
            # count = 0
            # for i in qtlist:
            #     table[count][0] = nodelinelist[count][0] #line number
            #     table[count][1] = i #query term
            #     table[count][2] = nodelinelist[count][1] #node
            #     count+=1

            # print(tabulate(table, headers=head, tablefmt="grid"))
            # print("Total number of query plans: "+str(len(self.query_plans)))
            # print(len(mapping))

            # print(ann_list)

            # res = "blockdiag { " + str(res[0]) + "}"

            # print(self.query_plans)

            # print(self.query_plans[0])

            # ann_list = traverse_qep(self.query_plans[0])

            # print(self.query_plans)

            loop_v = 0

            for plan in self.query_plans:
                # print(plan)

                tab1 = QtWidgets.QWidget()
                tab1.layout = QVBoxLayout()
                groupbox = QGroupBox("Annotation")
                groupbox.setObjectName = "Annotation"
                vbox = QVBoxLayout()
                groupbox.setLayout(vbox)
                TEXT = QTextEdit()
                TEXT.setReadOnly(True)

                test = traverse_qep(self.query_plans[loop_v], "")

                #print(test)
                TEXT.setText(test)
        
                BUTTON = QPushButton("Display Physical Query Plan")

                BUTTON.clicked.connect(partial(self.displayDiag, loop_v))
                vbox.addWidget(TEXT)
                self.AddToTab(tab1, groupbox)
                self.AddToTab(tab1, BUTTON)
                tab1.setLayout(tab1.layout)
                # tabs are being added also during 2nd execution of query
                if loop_v == 0:
                    self.tW.addTab(tab1, "QEP")
                else:
                    self.tW.addTab(tab1, "AEP " + str(loop_v))

                loop_v += 1

                print("XD")

            # print("Total number of query plans: "+str(len(query_plans)))

            # qep_relation and aqp_relations are used to store relations to be used for blockdiag
            ## sample relation for a single blockdiag
            # ["'1)Limit'  <- '2)Aggregate'  <- '3)Sort'  <- '4)Nested Loop'  <- '5)Index Scan';",
            #  "'1)Limit'  <- '2)Aggregate'  <- '3)Sort'  <- '4)Nested Loop'  <- '5)Bitmap Heap Scan'  <- '6)Bitmap Index Scan';"]
            # self.annotation1.setText(str(records))

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            self.TerminateConnectionToPostgreSQL()


# Start GUI Threadz

def GUI():

    if QtCore.QT_VERSION >= 0x50501:
        def excepthook(type_, value, traceback_):
            traceback.print_exception(type_, value, traceback_)
            QtCore.qFatal('')

        sys.excepthook = excepthook

    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()

    sys.exit(app.exec_())
    app.exec()

#Graph checker (generator): http://interactive.blockdiag.com/

# Documentation: http://blockdiag.com/en/blockdiag/introduction.html#setup
# How to embed in pyt: https://stackoverflow.com/questions/67652887/how-to-write-python-code-to-use-blockdiag-package
# Symbols: https://www.guru99.com/relational-algebra-dbms.html#14