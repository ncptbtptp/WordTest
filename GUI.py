#encoding=gb2312
##
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QMessageBox,
    QWidget,
    QPushButton,
    QMainWindow,
    QLabel,
    QLineEdit,  # for single line only
    QTextEdit,  # multi-lines support
    QPlainTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QToolBar,
    QStatusBar,
    QCheckBox,
    QToolButton,
    QDialog,
    QTableWidget,
    QTableWidgetItem,
    QProgressBar,
    QFileDialog,
    QGridLayout,
    QHeaderView
)
from PyQt6 import QtGui
from PyQt6.QtGui import QColor, QFont, QPalette, QAction, QIcon
import pyqtgraph as pg
import datetime
import os
import docx

import pprint
import sys
import WordDB
import win32api, win32con

class CustomDataValidator(QtGui.QValidator):
    # Must override super "validate"
    def validate(self, input, pos):
        print("custom validate called, ", input, pos)

        # Accepted
        if len(input) == 1 and input[0].islower():
            return (QtGui.QValidator.State.Acceptable, input, pos)
        # Denied
        else:
            return (QtGui.QValidator.State.Invalid, input, pos)

class Color(QWidget):
    def __init__(self, color):
        super().__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setPalette(palette)



class MainWindow(QMainWindow):
    def __del__(self):
        self.db.close()

    def __init__(self):
        super().__init__()

        self.db = WordDB.CWordsDB(r"F:\repos\WordTest\dictionary.db")
        self.db.open()
        self.today = str(datetime.date.today()) 

        self.setWindowTitle("���ֲ���V0.1")
        label = QLabel("��ӭ����ԶС����!")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        """
        edit = QLineEdit()
        #edit.setMaxLength(10)
        edit.setInputMask('<A')
        #edit.setValidator(CustomDataValidator())

        widget = Color("red")
        """
        self.setCentralWidget(label)

        toolbar = QToolBar("My main toolbar")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)

        button_action = QAction(QIcon("resource/fugue-icons-3.5.6/icons/address-book--pencil.png"), "���ֲ���", self)
        button_action.setStatusTip("���ֲ���")
        button_action.triggered.connect(self.onNewCharactersTest)
        #button_action.setCheckable(True)
        toolbar.addAction(button_action)

        toolbar.addSeparator()

        button_action3 = QAction(QIcon("resource/fugue-icons-3.5.6/icons/address-book--plus.png"), "���ʶ��", self)
        button_action3.setStatusTip("���ʶ��")
        button_action3.triggered.connect(self.onAddLearned)
        #button_action3.setCheckable(True)
        toolbar.addAction(button_action3)        

        #toolbar.addSeparator()

        button_action4 = QAction(QIcon("resource/fugue-icons-3.5.6/icons/address-book--minus.png"), "ɾ��ʶ��", self)
        button_action4.setStatusTip("ɾ��ʶ��")
        button_action4.triggered.connect(self.onRemoveLearned)
        #button_action4.setCheckable(True)
        toolbar.addAction(button_action4)       
        
        toolbar.addSeparator()

        button_action2 = QAction(QIcon("resource/fugue-icons-3.5.6/icons-shadowless/chart.png"), "ʶ�ֲַ�", self)
        button_action2.setStatusTip("ʶ�ֲַ�")
        button_action2.triggered.connect(self.onShowHistogram)
        #button_action2.setCheckable(True)
        toolbar.addAction(button_action2)

        button_action5 = QAction(QIcon("resource/fugue-icons-3.5.6/icons/magnifier-zoom-actual.png"), "ʶ�ֱ�", self)
        button_action5.setStatusTip("ʶ�ֱ�")
        button_action5.triggered.connect(lambda: self.onShowTable(self))
        toolbar.addAction(button_action5)

        button_action6 = QAction(QIcon("resource/fugue-icons-3.5.6/icons/magnifier-zoom.png"), "���ֱ�", self)
        button_action6.setStatusTip("���ֱ�")
        button_action6.triggered.connect(lambda: self.onShowNewCharsTable(self))
        toolbar.addAction(button_action6)

        toolbar.addSeparator()

        button_action7 = QAction(QIcon("resource/fugue-icons-3.5.6/icons/book-open.png"), "�������׶ȼ��", self)
        button_action7.setStatusTip("�������׶ȼ��")
        button_action7.triggered.connect(lambda: self.onPassageCheckTable(self))
        toolbar.addAction(button_action7)

        #toolbar.addWidget(QLabel("��ӭ������ԶС���ѣ�"))
        self.setStatusBar(QStatusBar(self))

        toolbar.addSeparator()
        toolbar.addWidget(QCheckBox())

        toolbar.addSeparator()
        toolbar.addWidget(QToolButton())

        toolbar.addSeparator()
        button_action3 = QAction(self.today, self)
        toolbar.addAction(button_action3)


        #toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        file_menu.addAction(button_action)

    def onSelectFolder(self, parent, lineEdit):
        dir_path = QFileDialog.getExistingDirectory(parent, "ѡ�����£�.docx�������ļ���", os.getcwd())
        lineEdit.setText(dir_path)
        lineEdit.setFocus()
        parent.setFocus()

    def checkOnePassage(self, file_path, new_chars_dict, learned_chars_set):
        # �ѵ�ǰ�ļ����ַ���ɨ�����
        doc = docx.Document(file_path)

        fullText = ""
        for para in doc.paragraphs:
            fullText += para.text

        # Filtering out non-Chinese characters
        ChineseText = ""
        for char in fullText:
            if char in new_chars_dict or char in learned_chars_set:
                ChineseText += char

        # ���� -> [����Ƶ�ʡ��Ѷ�]
        new_chars_in_text = {}
        # ���� -> ����Ƶ��
        learned_chars_in_text = {}

        # �ܹ��������������ظ���
        total = len(ChineseText)
        # ���ظ�
        total_new = 0
        total_learned = 0

        # ����ÿ�����֣�����: [���֡�����Ƶ�ʡ��Ѷ�]
        # ����ÿ�����֣�����: [���֡�����Ƶ��]
        for char in ChineseText:
            # ����ú�������ƪ�������Ѿ����ֹ�������Ƶ��
            if char in learned_chars_in_text:
                total_learned += 1
                learned_chars_in_text[char] += 1
            elif char in new_chars_in_text:
                total_new += 1
                new_chars_in_text[char][0] += 1
            elif char in learned_chars_set:
                total_learned += 1
                learned_chars_in_text[char] = 1
            else:
                total_new += 1
                new_chars_in_text[char] = [1, new_chars_dict[char]]
            
        return total, total_new, total_learned, new_chars_in_text.items(), learned_chars_in_text.items()

    def file_is_hidden(self, p):
        if os.name== 'nt':
            attribute = win32api.GetFileAttributes(p)
            return attribute & (win32con.FILE_ATTRIBUTE_HIDDEN | win32con.FILE_ATTRIBUTE_SYSTEM)
        else:
            return p.startswith('.') #linux-osx

    # �����Χ������
    #def is_Chinese_character(self, character):
    #    return (character > u'\u4e00' and character < u'\u9fff') or (character >= u'\ue81a' and character <= u'\u')

    def updatePassageTable(self, lineEdit, table):
        # Just need to scan DB once before each batch update
        # ��������dict:  ����->�Ѷ�
        all_new_dict = {character: coverage for character, frequency, coverage in self.db.dict_stats_new_characters_all_info()}
        # ��������set:  ����
        all_learned_set = {character[0] for character in self.db.learned_all()}

        search_dir = lineEdit.text()

        table.clearContents()

        files = [os.path.join(search_dir, f) for f in os.listdir(search_dir) if not self.file_is_hidden(os.path.join(search_dir, f)) and f.endswith(".docx")]
        #print(files)

        table.setRowCount(len(files))
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(['����', 'ʶ����', '������', '���֣�������', '���֣�������'])
        #table.resizeColumnsToContents()
        #table.resizeRowsToContents()


        new_chars_cache = []
        learned_chars_cache = []

        def inner_get_freq(elem):
            return elem[1]

        def inner_show_new_chars_table():
            if not new_chars_cache:
                return

            total_chars = int(table.item(table.currentRow(), 2).text())
            column_learned = table.item(table.currentRow(), 4).text()
            total_learned = int(column_learned[column_learned.find("(")+1 : column_learned.find(")")])
            total_new = total_chars - total_learned

            new_chars = new_chars_cache[table.currentRow()]
            passage_name = table.item(table.currentRow(), 0).text()
            #ratio = table.item(table.currentRow(), 1).value()
            ratio = table.cellWidget(table.currentRow(), 1).value()

            new_chars_table = QTableWidget()
            new_chars_table.clearContents()
            new_chars_table.setRowCount(len(new_chars))
            new_chars_table.setColumnCount(4)
            new_chars_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
            new_chars_table.setHorizontalHeaderLabels(['����', '����Ƶ��', '�Ѷ�', '�����ʶ'])

            bar2 = QProgressBar()

            def inner_update_ratio(s):

                #state = new_chars_table.cellWidget(new_chars_table.currentRow(), 3).layout().itemAt(0).widget().checkState()
                state = new_chars_table.cellWidget(new_chars_table.currentRow(), 3).checkState()
                new_freq = int(new_chars_table.item(new_chars_table.currentRow(), 1).text())

                nonlocal total_new

                if state == Qt.CheckState.Checked:
                    total_new -= new_freq
                else:
                    total_new += new_freq
                
                new_ratio = int(((total_chars - total_new) / total_chars) * 100)
                bar2.setValue(new_ratio)

            #print(table.currentRow(), table.currentColumn())

            # convert from dict to list
            new_chars_list = [[x[0], x[1][0], f"{int(x[1][1])}%"] for x in new_chars]

            # sort by frequency
            new_chars_list.sort(key=inner_get_freq, reverse=True)

            row = 0
            for r in new_chars_list:
                col = 0
                for item in r:
                    cell = QTableWidgetItem(str(item))
                    cell.setFlags(Qt.ItemFlag.ItemIsSelectable);
                    cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    new_chars_table.setItem(row, col, cell)
                    col += 1

                # Set the last check box
                chkbox = QCheckBox(new_chars_table)
                chkbox.setCheckState(Qt.CheckState.Unchecked)
                chkbox.stateChanged.connect(inner_update_ratio)

                # ����CSSҲ����Ψһ�ķ���
                # Ĭ��checkbox��table cell�п���಻���У����ʹ�������checkbox->layout->widget->cell�ķ�ʽ�����Ծ��У�����ѡ��checkbox������ѡ������cell����
                # ���Ե���slot��currentRow()��currentColumn()����-1��
                chkbox.setStyleSheet("padding-left: 43px;")
                new_chars_table.setCellWidget(row, col, chkbox)

                #chkbox_widget = QWidget(new_chars_table)
                #chkbox_layout = QHBoxLayout(chkbox_widget)
                #chkbox = QCheckBox(new_chars_table)
                #chkbox.setCheckState(Qt.CheckState.Unchecked)
                #chkbox.stateChanged.connect(inner_update_ratio)
                #chkbox_layout.addWidget(chkbox)
                #chkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                #chkbox_widget.setLayout(chkbox_layout)
                #new_chars_table.setCellWidget(row, col, chkbox_widget)

                

                row += 1

            #new_chars_table.resizeColumnsToContents()
            #new_chars_table.resizeRowsToContents()

            dlg = QDialog(self)
            dlg.setWindowTitle(f"��{passage_name}�����ֱ�")
            dlg.resize(700, 500)
            layout = QVBoxLayout()
            layout.addWidget(new_chars_table)

            bar1 = QProgressBar()
            bar1.setValue(ratio)
            bar1.setAlignment(Qt.AlignmentFlag.AlignCenter)

            layout2 = QHBoxLayout()
            layout2.addWidget(QLabel("ʶ����"))

            bar2.setValue(ratio)
            bar2.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout2.addWidget(bar2)

            layout.addLayout(layout2)

            dlg.setLayout(layout)
            dlg.exec()

        row = 0
        for file_path in files:
            total, total_new, total_learned, new_chars, learned_chars = self.checkOnePassage(file_path, all_new_dict, all_learned_set)

            # Cache for later click!
            new_chars_cache.append(new_chars)
            learned_chars_cache.append(learned_chars)

            # ������
            file_name = os.path.basename(file_path)
            item = QTableWidgetItem(file_name)
            item.setFlags(Qt.ItemFlag.ItemIsSelectable);
            table.setItem(row, 0, item)

            # ʶ����
            ratio = int((total_learned / total)*100)
            #table.setItem(row, 1, QTableWidgetItem(str(ratio) + "%"))

            bar = QProgressBar(table)
            bar.setValue(ratio)
            bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setCellWidget(row, 1, bar)

            # ������
            item = QTableWidgetItem(str(total))
            item.setFlags(Qt.ItemFlag.ItemIsSelectable);
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, 2, item)

            # ����
            #table.setItem(row, 2, QTableWidgetItem(str(len(new_chars))))
            btn1 = QPushButton(table)
            btn1.setText(f"{len(new_chars)} ({total_new})")
            table.setCellWidget(row, 3, btn1)
            btn1.clicked.connect(inner_show_new_chars_table)

            # ����
            item = QTableWidgetItem(f"{len(learned_chars)} ({total_learned})")
            item.setFlags(Qt.ItemFlag.ItemIsSelectable);
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, 4, item)
            #btn2 = QPushButton(table)
            #btn2.setText(f"{len(learned_chars)} ({total_learned})")
            #table.setCellWidget(row, 4, btn2)

            row += 1


            




    def onPassageCheckTable(self, s):
        dlg = QDialog(self)
        dlg.setWindowTitle(f"��������")
        dlg.resize(700, 500)

        lineEdit = QLineEdit()
        

        folderBtn = QPushButton()
        folderBtn.setText('ѡ���ļ���')
        folderBtn.clicked.connect(lambda: self.onSelectFolder(dlg, lineEdit))

        grid = QHBoxLayout()
        grid.addWidget(lineEdit)
        grid.addWidget(folderBtn)


        

        # Select a directory where all .docx files are saved

        table = QTableWidget()

        #bar = QProgressBar(table)
        #bar.setValue(50)
        #bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        #table.setCellWidget(0, 1, bar)
        
        #btn = QPushButton(table)
        #btn.setText('')
        #table.setCellWidget(0, 3, btn)


        # editingFinished is better than returnPressed: (When you press ��Enter�� or the field loses focus)
        lineEdit.editingFinished.connect(lambda: self.updatePassageTable(lineEdit, table))

        # Must be called after setRowCount/setColumnCount!
        #table.setHorizontalHeaderLabels(['����','����ʱ��'])
        
        # Read all learned characters out from database
        #new = self.db.dict_stats_new_characters_all_info()
        #new_count = len(new)

        #dlg.setWindowTitle(f"���ֱ�{new_count}��")

        ## Fill table data from database
        #table_data = []
        #for record in new:
        #    table_data.append([record[0], record[1], record[2]])

        #def configure_table(table_data_in, rows_in):
        #    # Configure the table
        #    table.clearContents()
        #    table.setRowCount(rows_in)
        #    table.setColumnCount(3)
        #    table.setHorizontalHeaderLabels(['����', '���׶�', '��ϸ'])

        #    row = 0
        #    for r in table_data_in:
        #        col = 0
        #        for item in r:
        #            cell = QTableWidgetItem(str(item))
        #            table.setItem(row, col, cell)
        #            col += 1
        #        row += 1

        #    table.resizeColumnsToContents()
        #    table.resizeRowsToContents()

        #configure_table(table_data, new_count)

        #table.show()

        layout = QVBoxLayout()
        #layout.addWidget(search)
        layout.addLayout(grid)
        layout.addWidget(table)

        dlg.setLayout(layout)
        dlg.exec()

    def onAddCharsButtonClicked(self, plainEditCtrl, parentDlg):
        contents = plainEditCtrl.toPlainText()
        if not contents:
            parentDlg.close()
            return

        box = QMessageBox()
        box.setWindowTitle("ȷ����ӣ�")
        box.setIcon(QMessageBox.Icon.Warning)
        box.setText(contents)
        box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No);
        ans = box.exec()

        if ans == QMessageBox.StandardButton.Yes:
            for character in contents:
                self.db.learned_insert_record(character, self.today)
                self.db.save()
            parentDlg.close()

    def onAddLearned(self, s):
        dlg = QDialog(self)
        dlg.setWindowTitle("���ʶ��")
        dlg.resize(500, 300)

        edit_contents = QPlainTextEdit()
        edit_contents.setFont(QFont('����', 15))

        button = QPushButton("ȷ��")
        button.setFont(QFont('����', 18))
        button.clicked.connect(lambda: self.onAddCharsButtonClicked(edit_contents, dlg))

        layout = QVBoxLayout()
        layout.addWidget(edit_contents)
        layout.addWidget(button)

        dlg.setLayout(layout)
        dlg.exec()

    def onRemoveCharsButtonClicked(self, plainEditCtrl, parentDlg):
        contents = plainEditCtrl.toPlainText()
        if not contents:
            parentDlg.close()
            return

        #dlg = QDialog(self)
        #dlg.setWindowTitle("ȷ��ɾ����")

        #label = QLabel(contents, dlg)
        #buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        #buttons.accepted.connect(self.onConfirmToRemoveChars)
        #buttons.rejected.connect(self.onRejectToRemoveChars)

        #layout = QVBoxLayout()
        #layout.addWidget(label)
        #layout.addWidget(buttons)

        #dlg.setLayout(layout)
        #dlg.exec()

        box = QMessageBox()
        box.setWindowTitle("ȷ��ɾ����")
        box.setIcon(QMessageBox.Icon.Warning)
        box.setText(contents)
        box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No);
        ans = box.exec()

        if ans == QMessageBox.StandardButton.Yes:
            for character in contents:
                self.db.learned_delete_record(character)
                self.db.save()
            parentDlg.close()


    def onRemoveLearned(self, s):
        dlg = QDialog(self)
        dlg.setWindowTitle("ɾ��ʶ��")
        dlg.resize(500, 300)

        #label_caption = QLabel()
        #label_caption.setFont(QFont('����', 12))
        #label_caption.setText("��������Ҫɾ���ĺ��֣�ɾ�����Ϊ���֣���")

        edit_contents = QPlainTextEdit()
        edit_contents.setFont(QFont('����', 15))

        #font.setBold(True)

        button = QPushButton("ȷ��")
        #button_yes.resize(50, 50)
        button.setFont(QFont('����', 18))
        #button_yes.setStyleSheet("background-color: green; color: white; border: 1px solid;")
        #button_yes.setStyleSheet("border: 3px solid green;")
        #button.move(160, 230)

        button.clicked.connect(lambda: self.onRemoveCharsButtonClicked(edit_contents, dlg))



        layout = QVBoxLayout()
        #layout.addWidget(label_caption)
        layout.addWidget(edit_contents)
        layout.addWidget(button)

        dlg.setLayout(layout)

        dlg.exec()

    def onNewCharactersTest(self, s):
        # ���Կ�ʼ������е����֣��Զ�����ʹ��Ƶ�ʸߵ�����
        self.characters = self.db.dict_stats_new_characters()
        self.char_index = 0
        self.learned_count = self.db.learned_stats_total()

        dlg = QDialog(self)
        dlg.setWindowTitle("���ֲ���")
        dlg.resize(500, 300)

        layoutH = QHBoxLayout()
        layoutV = QVBoxLayout()

        self.label_char = QLabel(dlg)
        self.label_char.setFont(QFont('����', 80))
        #label_char.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        #label_char.resize(150, 150)
        self.label_char.setText(self.characters[self.char_index])
        self.label_char.move(200, 10)
        #label_char.setGeometry(200, 10, 100, 100)
        #label_char.resize(100, 100)

        self.label_learned = QLabel(dlg)
        self.label_learned.setFont(QFont('����', 15))
        #label_learned.resize(150, 150)
        self.label_learned.setText(f"[����ʶ�� {self.learned_count}]")
        #label_learned.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_learned.move(190, 180)

        font = QFont('open-sans', 18)
        font.setBold(True)

        button_yes = QPushButton("��", dlg)
        #button_yes.resize(50, 50)
        button_yes.setFont(font)
        #button_yes.setStyleSheet("background-color: green; color: white; border: 1px solid;")
        #button_yes.setStyleSheet("border: 3px solid green;")
        button_yes.move(160, 230)
        button_yes.clicked.connect(self.onYesButtonClicked)

        button_no = QPushButton("��", dlg)
        #button_no.resize(50, 50)
        button_no.setFont(font)
        #button_no.setStyleSheet("background-color: red; color: white; border: 1px solid;")
        button_no.move(270, 230)
        button_no.clicked.connect(self.onNoButtonClicked)

       
        dlg.exec()

     #def onNewCharactersTest(self, s):
     #   dlg = QDialog(self)
     #   dlg.setWindowTitle("���ֲ���")
     #   dlg.resize(500, 300)

     #   layoutH = QHBoxLayout()
     #   layoutV = QVBoxLayout()

     #   label_char = QLabel()#QLabel(dlg)
     #   label_char.setFont(QFont('����', 80))
     #   label_char.setAlignment(Qt.AlignmentFlag.AlignCenter)
     #   #label_char.resize(150, 150)
     #   label_char.setText("��")

     #   label_learned = QLabel()
     #   label_learned.setFont(QFont('����', 15))
     #   #label_learned.resize(150, 150)
     #   label_learned.setText("[����ʶ�� 20]")
     #   label_learned.setAlignment(Qt.AlignmentFlag.AlignCenter)

     #   button_yes = QPushButton("��ʶ")
     #   button_yes.resize(200, 100)
     #   button_no = QPushButton("����ʶ")
     #   layoutH.addWidget(button_yes)
     #   layoutH.addWidget(button_no)

     #   layoutV.addWidget(label_char)
     #   layoutV.addLayout(QHBoxLayout())
     #   layoutV.addWidget(label_learned)
     #   layoutV.addLayout(layoutH)

     #   dlg.setLayout(layoutV)

     #   #button_yes1 = QPushButton("", dlg)
     #   #button_yes1.setGeometry(200, 150, 100, 100)
     #   #button_yes1.setStyleSheet("border-radius:50; border:1px solid black; background-image:url(resource/smile.jpg);")
        

     #   dlg.exec()

    def onShowNewCharsTable(self, parent):
        dlg = QDialog(self)
        dlg.resize(700, 500)

        table = QTableWidget()
        # Must be called after setRowCount/setColumnCount!
        #table.setHorizontalHeaderLabels(['����','����ʱ��'])
        
        # Read all learned characters out from database
        new = self.db.dict_stats_new_characters_all_info()
        new_count = len(new)

        dlg.setWindowTitle(f"���ֱ�{new_count}��")

        # Fill table data from database
        table_data = []
        for record in new:
            table_data.append([record[0], record[1], record[2]])

        def configure_table(table_data_in, rows_in):
            # Configure the table
            table.clearContents()
            table.setRowCount(rows_in)
            table.setColumnCount(3)
            table.setHorizontalHeaderLabels(['����', 'ʹ�ô���', '������'])

            row = 0
            for r in table_data_in:
                col = 0
                for item in r:
                    cell = QTableWidgetItem(str(item))
                    table.setItem(row, col, cell)
                    col += 1
                row += 1

            table.resizeColumnsToContents()
            table.resizeRowsToContents()

        configure_table(table_data, new_count)

        #table.show()

        def search_new_character(characters_db, edit):

            # ���������Ϊ�գ�����ʾ��������
            if not edit.text():
                configure_table(table_data, new_count)
            else:
                res = characters_db.dict_new_search(edit.text())
                rows = len(res)

                new_table_data = [[character, frequency, coverage] for character, frequency, coverage in res]
                configure_table(new_table_data, rows)

        search = QLineEdit()
        search.returnPressed.connect(lambda: search_new_character(self.db, search))

        layout = QVBoxLayout()
        layout.addWidget(search)
        layout.addWidget(table)

        dlg.setLayout(layout)
        dlg.exec()

    def onShowTable(self, parent):
        dlg = QDialog(self)
        dlg.resize(700, 500)

        table = QTableWidget()
        # Must be called after setRowCount/setColumnCount!
        #table.setHorizontalHeaderLabels(['����','����ʱ��'])
        
        # Read all learned characters out from database
        learned = self.db.learned_all()
        learned_count = len(learned)

        dlg.setWindowTitle(f"ʶ�ֱ�{learned_count}��")

        # Fill table data from database
        table_data = []
        for record in learned:
            table_data.append([record[0], record[1]])

        def configure_table(table_data_in, rows_in):
            # Configure the table
            table.clearContents()
            table.setRowCount(rows_in)
            table.setColumnCount(2)
            table.setHorizontalHeaderLabels(['����','ѧϰʱ��'])

            row = 0
            for r in table_data_in:
                col = 0
                for item in r:
                    cell = QTableWidgetItem(str(item))
                    table.setItem(row, col, cell)
                    col += 1
                row += 1

            table.resizeColumnsToContents()
            table.resizeRowsToContents()

        configure_table(table_data, learned_count)

        #table.show()

        def search_character(learned_db, edit):

            # ���������Ϊ�գ�����ʾ������ʶ�ĺ���
            if not edit.text():
                configure_table(table_data, learned_count)
            else:
                res = learned_db.learned_search(edit.text())
                rows = len(res)

                new_table_data = [[character, date] for character, date in res]
                configure_table(new_table_data, rows)

        search = QLineEdit()
        search.returnPressed.connect(lambda: search_character(self.db, search))

        layout = QVBoxLayout()
        layout.addWidget(search)
        layout.addWidget(table)

        dlg.setLayout(layout)
        dlg.exec()

    def onShowHistogram(self, s):
        dlg = QDialog(self)
        dlg.setWindowTitle("ʶ�����ֲ�ͼ")
        dlg.resize(700, 500)

        layoutH = QHBoxLayout()
        layoutV = QVBoxLayout()

        # �����ݿ��ж�ȡ
        learned_total = self.db.learned_stats_total()
        learned_stats = self.db.learned_stats_distribution()
        y1 = [learned for total, learned in learned_stats.values()]

        # creating a plot window
        plot = pg.plot()
        plot.setGeometry(100, 100, 300, 300)
        plot.setWindowTitle("")

        # create list for y-axis
        #y1 = [5, 5, 7, 10, 3, 8, 9, 1, 6, 2]
 
        # create horizontal list i.e x-axis
        #x = ['10%', '20%', '30%', '40%', '50%', '60%', '70%', '80%', '90%', '100%']
        #x = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        bargraph = pg.BarGraphItem(x = x, height = y1, width = 0.6, brush = 'g')
        # add item to plot window
        # adding bargraph item to the plot window
        plot.addItem(bargraph)

        label_text = ""
        label_text += f"00%-10%: {learned_stats[10][1]}/{learned_stats[10][0]}\n"
        label_text += f"10%-20%: {learned_stats[20][1]}/{learned_stats[20][0]}\n"
        label_text += f"20%-30%: {learned_stats[30][1]}/{learned_stats[30][0]}\n"
        label_text += f"30%-40%: {learned_stats[40][1]}/{learned_stats[40][0]}\n"
        label_text += f"40%-50%: {learned_stats[50][1]}/{learned_stats[50][0]}\n"
        label_text += f"50%-60%: {learned_stats[60][1]}/{learned_stats[60][0]}\n"
        label_text += f"60%-70%: {learned_stats[70][1]}/{learned_stats[70][0]}\n"
        label_text += f"70%-80%: {learned_stats[80][1]}/{learned_stats[80][0]}\n"
        label_text += f"80%-90%: {learned_stats[90][1]}/{learned_stats[90][0]}\n"
        label_text += f"90%-100%: {learned_stats[100][1]}/{learned_stats[100][0]}\n\n"
        label_text += f"��ʶ������{learned_total}"

        label_char = QLabel(dlg)
        label_char.setFont(QFont('����', 20))
        #label_char.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        label_char.resize(200, 200)
        label_char.setText(label_text)

        layoutH.addWidget(label_char)
        layoutH.addWidget(plot)

        dlg.setLayout(layoutH)
        dlg.exec()


    def onYesButtonClicked(self, s):
        # ��ǰ������ʶ��
        text = self.characters[self.char_index]
        self.db.learned_insert_record(text, self.today)
        self.db.save()

        # ����Ҫ�������ݿ�
        self.learned_count += 1

        # �ҵ���һ������
        self.char_index += 1
        if self.char_index >= len(self.characters):
            text = "�������"
        else:
            text = self.characters[self.char_index]

        self.label_char.setText(text)
        self.label_learned.setText(f"[����ʶ�� {self.learned_count}]")

    def onNoButtonClicked(self, s):
        # �ҵ���һ������
        self.char_index += 1
        if self.char_index >= len(self.characters):
            text = "�������"
        else:
            text = self.characters[self.char_index]

        self.label_char.setText(text)

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()

