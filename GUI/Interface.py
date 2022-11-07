from PyQt5 import QtWidgets, uic, Qt, QtSvg
import sys, psycopg2
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication
from blockdiag import parser, builder, drawer
from preprocessing import fetch_AQPS, process_QEP

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        uic.loadUi("MainUI.ui", self)

        self.setWindowTitle("Project 2")

        #Connect buttons to code
        self.connection_to_db.clicked.connect(self.ConnectSQL)
        self.sql_btn.clicked.connect(self.ExeSQLComm)
        self.dQp1.clicked.connect(self.displayDiag)

        self.SQL_Connection = 123

        self.show()


#SQL Connection
    def ConnectSQL(self):
        print("Clicked!")

        try:

            self.SQL_Connection = psycopg2.connect(
                host=self.ip_address.text(),
                database= self.db_n.text(),
                user= self.username.text(),
                password= self.password.text())

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        finally:
            if self.SQL_Connection is not None:
                self.status_d.setStyleSheet("color: green; font-weight: 600")
                self.status_d.setText("Connected!")

                self.sql_btn.setEnabled(True)

#Execute SQL Command
    def ExeSQLComm(self):
        try:

            self.c_r = self.SQL_Connection.cursor()

            QueryFromGUI = self.txt_sql.toPlainText()
            
            self.c_r.execute("EXPLAIN (ANALYZE, VERBOSE, FORMAT JSON)" + QueryFromGUI)

            records = self.c_r.fetchall()
            node_types_d = {}
            query_plans = []

            node_types,res,query_plans=process_QEP(records,query_plans,node_types_d)

            # fetching AQPS
            query_plans,aqp_relations = fetch_AQPS(self.c_r,node_types.keys(),QueryFromGUI,query_plans)
            print("Total number of query plans: "+str(len(query_plans)))  

            # qep_relation and aqp_relations are used to store relations to be used for blockdiag
            ## sample relation for a single blockdiag
            # ["'1)Limit'  <- '2)Aggregate'  <- '3)Sort'  <- '4)Nested Loop'  <- '5)Index Scan';",
            #  "'1)Limit'  <- '2)Aggregate'  <- '3)Sort'  <- '4)Nested Loop'  <- '5)Bitmap Heap Scan'  <- '6)Bitmap Index Scan';"]
            #self.annotation1.setText(str(records))

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

#Display diagram button
    def displayDiag(self, url):

        self.svgWidget = QtSvg.QSvgWidget('test.svg')

        self.svgWidget.show()




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
        #print("XD")
#
        #self.test.setPixmap(smaller_pixmap)
