# BERUFKOLLEG Lübbecke Des Kreises Minden-Lübbecke

# Die Programmierung wurde von: Omar Othman
# Datum: 2017.23.11


from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType
import sqlite3
import os
import sys
import time
scriptDir = os.path.dirname(os.path.realpath(__file__))
FROM_MAIN,_ = loadUiType(os.path.join(os.path.dirname(__file__),"main.ui"))
FROM_VIEW,_ = loadUiType(os.path.join(os.path.dirname(__file__),"view.ui"))
class Databases:
    def __init__(self):
        self.db = "berufskolleg.db"
        self.name = "termine"
        self.call = None
        self.commands = None
        self.folder = "AppBerufskolleg"
        self.path = os.path.join(os.path.expandvars("%userprofile%"), "Documents/")
    def from_path(self, name):
        return self.path+self.folder+"/"+name
    def connect(self, db):
        self.call = sqlite3.connect(db)
        self.commands = self.call.cursor()

    def create(self, db, values):
        try:
            self.commands.execute("create table if not exists " + db + " (" + values + ") ")
            self.call.commit()
            return True
        except sqlite3.Error as s:
            print(s)
            return False
        except sqlite3.DatabaseError as s:
            print(s)
            return False
        except sqlite3.DataError as s:
            print(s)
            return False

    def insert(self, db, value, values, insert=()):
        try:
            self.commands.execute("insert into " + db + " (" + value + ") VALUES " + values, insert)
            self.call.commit()
            return True
        except sqlite3.Error as s:
            print(s)
            return False
        except sqlite3.DatabaseError:
            return False
        except sqlite3.DataError:
            return False

    def update(self, db, name, to, where, value):
        try:
            self.commands.execute("update " + db + " set " + name + "=:to WHERE " + where + "=:value",
                                  {"to": to, "value": value})
            self.call.commit()
            return True
        except sqlite3.Error:
            return False
        except sqlite3.DatabaseError:
            return False
        except sqlite3.DataError:
            return False
    def update_with(self, db, name, to, where, value, _and, _to, __and, __to):
        try:
            self.commands.execute("update " + db + " set " + name + "=:to WHERE " + where + "=:value AND "+_and+"=:tto AND "+__and+"=:ttto",
                                  {"to": to, "value": value, "tto": _to, "ttto": __to})
            self.call.commit()
            return True
        except sqlite3.Error:
            return False
        except sqlite3.DatabaseError:
            return False
        except sqlite3.DataError:
            return False

    def enter_get_commands(self, commands, value=None):
        try:
            if value is None:
                self.commands.execute(commands)
                return self.commands.fetchall()
            else:
                self.commands.execute(commands, value)
                return self.commands.fetchall()
        except sqlite3.Error:
            return False
        except sqlite3.DatabaseError:
            return False
        except sqlite3.DataError:
            return False

    def enter_set_commands(self, commands, value=None):
        try:
            if value is None:
                self.commands.execute(commands)
                self.call.commit()
                return True
            else:
                self.commands.execute(commands, value)
                self.call.commit()
                return True
        except sqlite3.Error as e:
            print(e)
            return False
        except sqlite3.DatabaseError as e:
            print(e)
            return False
        except sqlite3.DataError as e:
            print(e)
            return False

    def get_all_data(self, db):
        try:
            self.commands.execute("select * from " + db)

            return self.commands.fetchall()
        except sqlite3.Error:
            return False
        except sqlite3.DatabaseError:
            return False
        except sqlite3.DataError:
            return False

    def delete(self, db, where, equals):
        try:
            self.commands.execute("delete from " + db + " WHERE " + where + "=:eq", {"eq": equals})
            self.call.commit()
            return True
        except sqlite3.Error:
            return False
        except sqlite3.DatabaseError:
            return False
        except sqlite3.DataError:
            return False

    def close(self):
        try:
            self.call.close()
            self.commands.close()
        except sqlite3.Error:
            return False
        except sqlite3.DatabaseError:
            return False
        except sqlite3.DataError:
            return False
class Main(QMainWindow, FROM_MAIN):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.default()
        self.make_db()
        self.name = None
        self.nachname = None
        self.datum = None
        self.table = None
        self.row_index = 0
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        db = Databases()
        if not os.path.exists(db.path+db.folder):
            try:
                os.makedirs(db.path+db.folder)
            except:
                QMessageBox.critical(self, "Falsch", "Bitte führen Sie die Anwendung über den Administrator aus. Zu erstellende Dateien")
        self.full_sqlite()
        self.sqlite_heute.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_suche.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_suche.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_suche.customContextMenuRequested.connect(self.on_menu_suche)
        self.sqlite_heute.setContextMenuPolicy(Qt.CustomContextMenu)
        self.sqlite_heute.customContextMenuRequested.connect(self.on_menu_sqlite)
        self.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableWidget.customContextMenuRequested.connect(self.on_menu_table)
        self.popMenu = QMenu(self)
        self.Qedit = QAction("edit", self)
        self.Qremove = QAction("remove", self)
        self.Qedit.triggered.connect(self.on_edit_clicked)
        self.Qremove.triggered.connect(self.on_remove_clicked)
        self.popMenu.addAction(self.Qedit)
        self.popMenu.addAction(self.Qremove)
    def get_time(self, t):
        if t<10:
            return str("0")+str(t)
        else:
            return str(t)
    def on_menu_suche(self, pos):
        s = self.table_suche.horizontalHeader().logicalIndexAt(pos)
        if s>1:
            return
        try:
            indexes = self.table_suche.selectedIndexes()[0].row()
            self.row_index = indexes
            self.table = self.table_suche
            name = self.table_suche.item(indexes, 0)
            self.name = name.text()
            self.nachname = self.table_suche.item(indexes, 1).text()
            self.datum = self.table_suche.item(indexes, 3).text()
        except:
            return
        self.popMenu.exec_(self.table_suche.mapToGlobal(pos))
    def on_menu_table(self, pos):
        s = self.tableWidget.horizontalHeader().logicalIndexAt(pos)
        if s>1:
            return
        try:
            indexes = self.tableWidget.selectedIndexes()[0].row()
            self.row_index = indexes
            self.table = self.tableWidget
            name = self.tableWidget.item(indexes, 0)
            self.name = name.text()
            self.nachname = self.tableWidget.item(indexes, 1).text()
            self.datum = self.tableWidget.item(indexes, 3).text()
        except:
            return
        self.popMenu.exec_(self.tableWidget.mapToGlobal(pos))
    def on_edit_clicked(self):
        #app=QApplication(sys.argv)
        view = View(self)
        view.set_view(self.row_index, self.table, self.datum, name=self.name, nachname=self.nachname)
        view.show()
        #app.exec_()
    def on_remove_clicked(self):
        db = Databases()
        db.connect(db.from_path(db.db))
        datum = self.datum.split(",")[0]
        db.enter_set_commands("delete from "+db.name+" where name=:na and nachname=:nach and datum=:dat", value={"na": self.name, "nach": self.nachname, "dat": datum})
        db.close()
        self.table.removeRow(self.row_index)
    def on_menu_sqlite(self, pos):
        s = self.sqlite_heute.horizontalHeader().logicalIndexAt(pos)
        if s>1:
            return
        try:
            indexes = self.sqlite_heute.selectedIndexes()[0].row()
            self.row_index = indexes
            self.table = self.sqlite_heute
            name = self.sqlite_heute.item(indexes, 0)
            self.name = name.text()
            self.nachname = self.sqlite_heute.item(indexes, 1).text()
            self.datum = self.sqlite_heute.item(indexes, 3).text()
        except:
            return
        self.popMenu.exec_(self.sqlite_heute.mapToGlobal(pos))  
    def full_sqlite(self):
        db = Databases()
        db.connect(db.from_path(db.db))
        raw = db.get_all_data(db.name)
        for data in raw:
            name = data[0]
            nachname = data[1]
            terminname = data[2]
            des = data[3]
            datum = data[4]
            stunde = data[5]
            status = data[6]
            self.add_to_termin(name, nachname, terminname, datum+", "+stunde, status)
            if self.is_today(datum):
                self.add_to_today(name, nachname, terminname, datum+", "+stunde, status)
    def is_today(self, datum):
        return time.strftime("%d/%m/%y") == datum
        
    def make_db(self):
        db = Databases()
        db.connect(db.from_path(db.db))
        db.create(db.name, "name text, nachname text, termin_name text, des text, datum text, stunde text, status")
        db.close()
    def add_to_termin(self, name, nachname, terminname, datum, status):
        pos = self.tableWidget.rowCount()
        self.tableWidget.insertRow(pos)
        self.tableWidget.setItem(pos, 0, QTableWidgetItem(name))
        self.tableWidget.setItem(pos, 1, QTableWidgetItem(nachname))
        self.tableWidget.setItem(pos, 2, QTableWidgetItem(terminname))
        self.tableWidget.setItem(pos, 3, QTableWidgetItem(datum))
        self.tableWidget.setItem(pos, 4, QTableWidgetItem(status))
    def add_to_today(self, name, nachname, terminname, datum, status):
        pos = self.sqlite_heute.rowCount()
        self.sqlite_heute.insertRow(pos)
        self.sqlite_heute.setItem(pos, 0, QTableWidgetItem(name))
        self.sqlite_heute.setItem(pos, 1, QTableWidgetItem(nachname))
        self.sqlite_heute.setItem(pos, 2, QTableWidgetItem(terminname))
        self.sqlite_heute.setItem(pos, 3, QTableWidgetItem(datum))
        self.sqlite_heute.setItem(pos, 4, QTableWidgetItem(status))
    def add_to_suche(self, name, nachname, terminname, datum, status):
        pos = self.table_suche.rowCount()
        self.table_suche.insertRow(pos)
        self.table_suche.setItem(pos, 0, QTableWidgetItem(name))
        self.table_suche.setItem(pos, 1, QTableWidgetItem(nachname))
        self.table_suche.setItem(pos, 2, QTableWidgetItem(terminname))
        self.table_suche.setItem(pos, 3, QTableWidgetItem(datum))
        self.table_suche.setItem(pos, 4, QTableWidgetItem(status))
    def default(self):
        self.setWindowTitle("BERUFSKOLLEG Lübbecke")
        self.setWindowIcon(QIcon(scriptDir + os.path.sep + 'logo.jpg'))
        self.button_speichen.clicked.connect(self.on_speichen_button_click)
        self.button_search.clicked.connect(self.on_suche_button_click)
        self.edit_name.setPlaceholderText("Erforderlich")
        self.edit_nachname.setPlaceholderText("Erforderlich")
        self.edit_terminname.setPlaceholderText("Erforderlich")
        self.edit_beschreibung.setPlaceholderText("Optional")
        self.edit_name_suche.setPlaceholderText("Erforderlich")
        self.edit_nachname_suche.setPlaceholderText("Erforderlich")
    def on_speichen_button_click(self):
        name = self.edit_name.text()
        nachname = self.edit_nachname.text()
        termin_name = self.edit_terminname.text()
        des = self.edit_beschreibung.toPlainText()
        tag = self.spin_tag.value()
        monate = self.spin_monat.value()
        jahr = self.spin_jahr.value()
        stund = self.spin_stunde.value()
        minu = self.spin_min.value()
        if not name or not nachname or not termin_name:
            QMessageBox.critical(self, "Falsch", "Bitte füllen Sie die folgenden Felder aus:\nName, Nachname, Terminname")
            return
        else:
            datum = str(self.get_time(tag))+"/"+str(self.get_time(monate))+"/"+str(jahr)
            stu = str(self.get_time(stund))+":"+str(self.get_time(minu))
            db = Databases()
            db.connect(db.from_path(db.db))
            db.insert(db.name, "name, nachname, termin_name, des, datum, stunde, status", "(?, ?, ?, ?, ?, ?, ?)",
                      insert=(name, nachname, termin_name, des, datum, stu, "noch nicht"))
            db.close()
            self.add_to_termin(name, nachname, termin_name, datum+","+stu, "noch nicht")
            QMessageBox.information(self, "Geschehen", "Erfolgreich gespeichert")
        
    def on_suche_button_click(self):
        self.table_suche.setRowCount(0);
        name = self.edit_name_suche.text()
        nachname = self.edit_nachname_suche.text()
        if not name or not nachname:
            QMessageBox.critical(self, "Falsch", "Bitte füllen Sie die folgenden Felder aus:\nName, Nachname")
            return
        else:
            db = Databases()
            db.connect(db.from_path(db.db))
            raw = db.enter_get_commands("select * from "+db.name+" where name=:na and nachname=:nach", value={"na": name, "nach": nachname})
            if not raw:
                QMessageBox.information(self, "Geschehen", "Nicht gefunden!")
                return
            for data in raw:
                name = data[0]
                nachname = data[1]
                terminname = data[2]
                des = data[3]
                datum = data[4]
                stunde = data[5]
                self.add_to_suche(name, nachname, terminname, datum+", "+stunde, "noch nicht")
                
class View(QMainWindow, FROM_VIEW):
    def __init__(self, parent=None):
        super(View, self).__init__(parent)
        #QMainWindow.__init__(self)
        self.setupUi(self)
        self.row = None
        self.name = None
        self.datum = None
        self.nachname = None
        self.status.addItem("noch nicht")
        self.status.addItem("nich gekommen")
        self.status.addItem("gekommen")
        self.status.addItem("hat ein Medizinblatt")
        self.button_ends.clicked.connect(self.make_ex)
        self.button_save.clicked.connect(self.save_db)
        
    def make_ex(self):
        self.destroy()
    def set_view(self, row, table, datum, name=None, nachname=None):
        self.name = name
        self.nachname = nachname
        self.datum = datum
        self.row = row
        self.table = table
        self.build_view()
    def build_view(self):
        db = Databases()
        db.connect(db.from_path(db.db))
        if self.datum:
            datum = self.datum.split(",")[0]
            raw = db.enter_get_commands("select * from "+db.name+" where name=:na and nachname=:nach and datum=:da", value={"na": self.name, "nach": self.nachname, "da": datum})
            if raw:
                terminname = raw[0][2]
                des = raw[0][3]
                status = raw[0][6]
                if status == "noch nicht":
                    self.status.setCurrentText("noch nicht")
                if status == "nich gekommen":
                    self.status.setCurrentText("nich gekommen")
                if status == "gekommen":
                    self.status.setCurrentText("gekommen")
                if status == "hat ein Medizinblatt":
                    self.status.setCurrentText("hat ein Medizinblatt")
                self.edit_name.setText(self.name)
                self.edit_nachname.setText(self.nachname)
                self.edit_termin_name.setText(terminname)
                self.edit_deschr.insertPlainText(des)
    def add_to_today(self, name, nachname, terminname, datum, status):
        pos = self.table.rowCount()
        self.table.insertRow(pos)
        self.table.setItem(pos, 0, QTableWidgetItem(name))
        self.table.setItem(pos, 1, QTableWidgetItem(nachname))
        self.table.setItem(pos, 2, QTableWidgetItem(terminname))
        self.table.setItem(pos, 3, QTableWidgetItem(datum))
        self.table.setItem(pos, 4, QTableWidgetItem(status))
    def save_db(self):
        datum = self.datum.split(",")[0]
        name = self.edit_name.text()
        nachname = self.edit_nachname.text()
        terminname = self.edit_termin_name.text()
        des = self.edit_deschr.toPlainText()
        status = self.status.currentText()
        db = Databases()
        db.connect(db.from_path(db.db))
        db.update_with(db.name, "name", name, "name", self.name, "nachname", self.nachname, "datum", datum)
        db.update_with(db.name, "nachname", nachname, "name", self.name, "nachname", self.nachname, "datum", datum)
        db.update_with(db.name, "des", des, "name", self.name, "nachname", self.nachname, "datum", datum)
        db.update_with(db.name, "termin_name", terminname, "name", self.name, "nachname", self.nachname, "datum", datum)
        db.update_with(db.name, "status", status, "name", self.name, "nachname", self.nachname, "datum", datum)
        self.table.removeRow(self.row)
        self.add_to_today(name, nachname, terminname, self.datum, status)
        QMessageBox.information(self, "Geschehen", "Erfolgreich gespeichert")
        self.make_ex()
def main():
    app=QApplication(sys.argv)
    window = Main()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()
