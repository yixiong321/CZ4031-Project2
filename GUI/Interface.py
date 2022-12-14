import traceback
from functools import partial

from PyQt5 import QtWidgets, uic, Qt, QtSvg, QtCore
import sys, psycopg2
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication, QVBoxLayout, QGroupBox, QTextEdit
from blockdiag import parser, builder, drawer
from preprocessing import fetch_AQPS, process_QEP
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


#SQL Connection

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

#Execute SQL Command

    def LoadQueriesToUI(self, _qList):

        counter = 0
        for query in _qList:
            self.qList.addItem("Example Query No. " + str(counter), query)
            counter += 1

    def ExeSQLComm(self):
        try:

            self.c_r = self.SQL_Connection.cursor()

            QueryFromGUI = self.txt_sql.toPlainText()
            
            self.c_r.execute("EXPLAIN (ANALYZE, VERBOSE, FORMAT JSON)" + QueryFromGUI)

            records = self.c_r.fetchall()
            node_types_d = {}
            self.query_plans = []

            node_types,res,self.query_plans=process_QEP(records,self.query_plans,node_types_d)

            #res = "blockdiag { " + str(res[0]) + "}"

            print(self.query_plans)

            # fetching AQPS
            self.query_plans,self.aqp_relations = fetch_AQPS(self.c_r,node_types.keys(),QueryFromGUI,self.query_plans)



            print(self.query_plans)


            loop_v = 0

            for plan in self.aqp_relations:
                print(plan)

                tab1 = QtWidgets.QWidget()
                tab1.layout = QVBoxLayout()
                groupbox = QGroupBox("Annotation")
                groupbox.setObjectName = "Annotation"
                vbox = QVBoxLayout()
                groupbox.setLayout(vbox)
                TEXT = QTextEdit()
                TEXT.setReadOnly(True)
                TEXT.setText("TEXT GOES HERE")
                BUTTON = QPushButton("Display Phisical Query Plan")
                BUTTON.clicked.connect(partial(self.displayDiag, loop_v))
                vbox.addWidget(TEXT)
                self.AddToTab(tab1, groupbox)
                self.AddToTab(tab1, BUTTON)
                tab1.setLayout(tab1.layout)

                if loop_v == 0:
                    self.tW.addTab(tab1, "QEP")
                else:
                    self.tW.addTab(tab1, "AEP " + str(loop_v))

                loop_v += 1


            #print("Total number of query plans: "+str(len(query_plans)))

            # qep_relation and aqp_relations are used to store relations to be used for blockdiag
            ## sample relation for a single blockdiag
            # ["'1)Limit'  <- '2)Aggregate'  <- '3)Sort'  <- '4)Nested Loop'  <- '5)Index Scan';",
            #  "'1)Limit'  <- '2)Aggregate'  <- '3)Sort'  <- '4)Nested Loop'  <- '5)Bitmap Heap Scan'  <- '6)Bitmap Index Scan';"]
            #self.annotation1.setText(str(records))

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    def AddToTab(self, tab, obj):
        tab.layout.addWidget(obj)

    #Display diagram button
    def displayDiag(self, number):

        print(self.aqp_relations[number])

        diag_string = self.aqp_relations[number]

        diag_string = "blockdiag {orientation = portrait" + str(diag_string[0]) + "}"

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



#Create SVG Diagram

data = """
blockdiag {
  orientation = portrait;

  A[label = "(Projection)"];
  B[label = "(Selection)"];
  C[label = "A conn B"];
  D[label = "Table TEST1"];
  E[label = "Table TEST2"];

  Z[label = "TEST !@#"];

  A -> B -> C -> D[dir = none];
       C -> E [dir = none];
       B -> Z [dir = none];
       A -> Z;
}
"""

#tree = parser.parse_string(data)

#diagram = builder.ScreenNodeBuilder.build(tree)
#
#diagram.set_default_fontfamily('sansserif-normal')
#
#draw = drawer.DiagramDraw('SVG', diagram, filename="foo.svg")
#draw.draw()
#draw.save()


def GUI():

    if QtCore.QT_VERSION >= 0x50501:
        def excepthook(type_, value, traceback_):
            traceback.print_exception(type_, value, traceback_)
            QtCore.qFatal('')

        sys.excepthook = excepthook


    app = QApplication(sys.argv)
    window = MainWindow()
    app.exec()


# Alernative? https://plantuml.com/

#Graph checker (generator): http://interactive.blockdiag.com/

# Documentation: http://blockdiag.com/en/blockdiag/introduction.html#setup
# How to embed in pyt: https://stackoverflow.com/questions/67652887/how-to-write-python-code-to-use-blockdiag-package
# Symbols: https://www.guru99.com/relational-algebra-dbms.html#14


#Old code:
        #img = Image.open('foo.png')
        #img.show()
#
        #pixmap = QPixmap('foo.png')
#
        #print(self.textV.width())
#
        #smaller_pixmap = pixmap.scaledToWidth(self.test.width())
#
#
        #self.test.setPixmap(smaller_pixmap)
