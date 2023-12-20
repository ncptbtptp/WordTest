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

        self.setWindowTitle("汉字测试V0.1")
        label = QLabel("欢迎赵新远小朋友!")
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

        button_action = QAction(QIcon("resource/fugue-icons-3.5.6/icons/address-book--pencil.png"), "生字测试", self)
        button_action.setStatusTip("生字测试")
        button_action.triggered.connect(self.onNewCharactersTest)
        #button_action.setCheckable(True)
        toolbar.addAction(button_action)

        toolbar.addSeparator()

        button_action3 = QAction(QIcon("resource/fugue-icons-3.5.6/icons/address-book--plus.png"), "添加识字", self)
        button_action3.setStatusTip("添加识字")
        button_action3.triggered.connect(self.onAddLearned)
        #button_action3.setCheckable(True)
        toolbar.addAction(button_action3)        

        #toolbar.addSeparator()

        button_action4 = QAction(QIcon("resource/fugue-icons-3.5.6/icons/address-book--minus.png"), "删除识字", self)
        button_action4.setStatusTip("删除识字")
        button_action4.triggered.connect(self.onRemoveLearned)
        #button_action4.setCheckable(True)
        toolbar.addAction(button_action4)       
        
        toolbar.addSeparator()

        button_action2 = QAction(QIcon("resource/fugue-icons-3.5.6/icons-shadowless/chart.png"), "识字分布", self)
        button_action2.setStatusTip("识字分布")
        button_action2.triggered.connect(self.onShowHistogram)
        #button_action2.setCheckable(True)
        toolbar.addAction(button_action2)

        button_action5 = QAction(QIcon("resource/fugue-icons-3.5.6/icons/magnifier-zoom-actual.png"), "识字表", self)
        button_action5.setStatusTip("识字表")
        button_action5.triggered.connect(lambda: self.onShowTable(self))
        toolbar.addAction(button_action5)

        button_action6 = QAction(QIcon("resource/fugue-icons-3.5.6/icons/magnifier-zoom.png"), "生字表", self)
        button_action6.setStatusTip("生字表")
        button_action6.triggered.connect(lambda: self.onShowNewCharsTable(self))
        toolbar.addAction(button_action6)

        toolbar.addSeparator()

        button_action7 = QAction(QIcon("resource/fugue-icons-3.5.6/icons/book-open.png"), "文章难易度检测", self)
        button_action7.setStatusTip("文章难易度检测")
        button_action7.triggered.connect(lambda: self.onPassageCheckTable(self))
        toolbar.addAction(button_action7)

        #toolbar.addWidget(QLabel("欢迎，赵新远小朋友！"))
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
        dir_path = QFileDialog.getExistingDirectory(parent, "选择文章（.docx）所在文件夹", os.getcwd())
        lineEdit.setText(dir_path)
        lineEdit.setFocus()
        parent.setFocus()

    def checkOnePassage(self, file_path, new_chars_dict, learned_chars_set):
        # 把当前文件中字符都扫描进来
        doc = docx.Document(file_path)

        fullText = ""
        for para in doc.paragraphs:
            fullText += para.text

        # Filtering out non-Chinese characters
        ChineseText = ""
        for char in fullText:
            if char in new_chars_dict or char in learned_chars_set:
                ChineseText += char

        # 汉字 -> [出现频率、难度]
        new_chars_in_text = {}
        # 汉字 -> 出现频率
        learned_chars_in_text = {}

        # 总共多少字数（记重复）
        total = len(ChineseText)
        # 记重复
        total_new = 0
        total_learned = 0

        # 对于每个生字，返回: [汉字、出现频率、难度]
        # 对于每个熟字，返回: [汉字、出现频率]
        for char in ChineseText:
            # 如果该汉字在这篇文章中已经出现过，更新频率
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

    # 这个范围不完整
    #def is_Chinese_character(self, character):
    #    return (character > u'\u4e00' and character < u'\u9fff') or (character >= u'\ue81a' and character <= u'\u')

    def updatePassageTable(self, lineEdit, table):
        # Just need to scan DB once before each batch update
        # 对于生字dict:  汉字->难度
        all_new_dict = {character: coverage for character, frequency, coverage in self.db.dict_stats_new_characters_all_info()}
        # 对于熟字set:  汉字
        all_learned_set = {character[0] for character in self.db.learned_all()}

        search_dir = lineEdit.text()

        table.clearContents()

        files = [os.path.join(search_dir, f) for f in os.listdir(search_dir) if not self.file_is_hidden(os.path.join(search_dir, f)) and f.endswith(".docx")]
        #print(files)

        table.setRowCount(len(files))
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(['文章', '识字率', '总字数', '生字（总数）', '熟字（总数）'])
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
            new_chars_table.setHorizontalHeaderLabels(['生字', '出现频率', '难度', '如果认识'])

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

                # 设置CSS也许是唯一的方法
                # 默认checkbox在table cell中靠左侧不居中；如果使用下面的checkbox->layout->widget->cell的方式，可以居中，但是选中checkbox并不会选中整个cell。。
                # 所以导致slot中currentRow()和currentColumn()都是-1。
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
            dlg.setWindowTitle(f"《{passage_name}》生字表")
            dlg.resize(700, 500)
            layout = QVBoxLayout()
            layout.addWidget(new_chars_table)

            bar1 = QProgressBar()
            bar1.setValue(ratio)
            bar1.setAlignment(Qt.AlignmentFlag.AlignCenter)

            layout2 = QHBoxLayout()
            layout2.addWidget(QLabel("识字率"))

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

            # 文章名
            file_name = os.path.basename(file_path)
            item = QTableWidgetItem(file_name)
            item.setFlags(Qt.ItemFlag.ItemIsSelectable);
            table.setItem(row, 0, item)

            # 识字率
            ratio = int((total_learned / total)*100)
            #table.setItem(row, 1, QTableWidgetItem(str(ratio) + "%"))

            bar = QProgressBar(table)
            bar.setValue(ratio)
            bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setCellWidget(row, 1, bar)

            # 总字数
            item = QTableWidgetItem(str(total))
            item.setFlags(Qt.ItemFlag.ItemIsSelectable);
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, 2, item)

            # 生字
            #table.setItem(row, 2, QTableWidgetItem(str(len(new_chars))))
            btn1 = QPushButton(table)
            btn1.setText(f"{len(new_chars)} ({total_new})")
            table.setCellWidget(row, 3, btn1)
            btn1.clicked.connect(inner_show_new_chars_table)

            # 熟字
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
        dlg.setWindowTitle(f"所有文章")
        dlg.resize(700, 500)

        lineEdit = QLineEdit()
        

        folderBtn = QPushButton()
        folderBtn.setText('选择文件夹')
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


        # editingFinished is better than returnPressed: (When you press ‘Enter’ or the field loses focus)
        lineEdit.editingFinished.connect(lambda: self.updatePassageTable(lineEdit, table))

        # Must be called after setRowCount/setColumnCount!
        #table.setHorizontalHeaderLabels(['汉字','加入时间'])
        
        # Read all learned characters out from database
        #new = self.db.dict_stats_new_characters_all_info()
        #new_count = len(new)

        #dlg.setWindowTitle(f"生字表（{new_count}）")

        ## Fill table data from database
        #table_data = []
        #for record in new:
        #    table_data.append([record[0], record[1], record[2]])

        #def configure_table(table_data_in, rows_in):
        #    # Configure the table
        #    table.clearContents()
        #    table.setRowCount(rows_in)
        #    table.setColumnCount(3)
        #    table.setHorizontalHeaderLabels(['文章', '难易度', '详细'])

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
        box.setWindowTitle("确认添加？")
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
        dlg.setWindowTitle("添加识字")
        dlg.resize(500, 300)

        edit_contents = QPlainTextEdit()
        edit_contents.setFont(QFont('楷体', 15))

        button = QPushButton("确定")
        button.setFont(QFont('黑体', 18))
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
        #dlg.setWindowTitle("确认删除吗？")

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
        box.setWindowTitle("确定删除？")
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
        dlg.setWindowTitle("删除识字")
        dlg.resize(500, 300)

        #label_caption = QLabel()
        #label_caption.setFont(QFont('黑体', 12))
        #label_caption.setText("请输入需要删除的汉字（删除后成为生字）：")

        edit_contents = QPlainTextEdit()
        edit_contents.setFont(QFont('楷体', 15))

        #font.setBold(True)

        button = QPushButton("确定")
        #button_yes.resize(50, 50)
        button.setFont(QFont('黑体', 18))
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
        # 测试开始获得所有的生字（自动按照使用频率高低排序）
        self.characters = self.db.dict_stats_new_characters()
        self.char_index = 0
        self.learned_count = self.db.learned_stats_total()

        dlg = QDialog(self)
        dlg.setWindowTitle("生字测试")
        dlg.resize(500, 300)

        layoutH = QHBoxLayout()
        layoutV = QVBoxLayout()

        self.label_char = QLabel(dlg)
        self.label_char.setFont(QFont('楷体', 80))
        #label_char.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        #label_char.resize(150, 150)
        self.label_char.setText(self.characters[self.char_index])
        self.label_char.move(200, 10)
        #label_char.setGeometry(200, 10, 100, 100)
        #label_char.resize(100, 100)

        self.label_learned = QLabel(dlg)
        self.label_learned.setFont(QFont('楷体', 15))
        #label_learned.resize(150, 150)
        self.label_learned.setText(f"[已认识： {self.learned_count}]")
        #label_learned.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_learned.move(190, 180)

        font = QFont('open-sans', 18)
        font.setBold(True)

        button_yes = QPushButton("√", dlg)
        #button_yes.resize(50, 50)
        button_yes.setFont(font)
        #button_yes.setStyleSheet("background-color: green; color: white; border: 1px solid;")
        #button_yes.setStyleSheet("border: 3px solid green;")
        button_yes.move(160, 230)
        button_yes.clicked.connect(self.onYesButtonClicked)

        button_no = QPushButton("×", dlg)
        #button_no.resize(50, 50)
        button_no.setFont(font)
        #button_no.setStyleSheet("background-color: red; color: white; border: 1px solid;")
        button_no.move(270, 230)
        button_no.clicked.connect(self.onNoButtonClicked)

       
        dlg.exec()

     #def onNewCharactersTest(self, s):
     #   dlg = QDialog(self)
     #   dlg.setWindowTitle("生字测试")
     #   dlg.resize(500, 300)

     #   layoutH = QHBoxLayout()
     #   layoutV = QVBoxLayout()

     #   label_char = QLabel()#QLabel(dlg)
     #   label_char.setFont(QFont('楷体', 80))
     #   label_char.setAlignment(Qt.AlignmentFlag.AlignCenter)
     #   #label_char.resize(150, 150)
     #   label_char.setText("好")

     #   label_learned = QLabel()
     #   label_learned.setFont(QFont('楷体', 15))
     #   #label_learned.resize(150, 150)
     #   label_learned.setText("[已认识： 20]")
     #   label_learned.setAlignment(Qt.AlignmentFlag.AlignCenter)

     #   button_yes = QPushButton("认识")
     #   button_yes.resize(200, 100)
     #   button_no = QPushButton("不认识")
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
        #table.setHorizontalHeaderLabels(['汉字','加入时间'])
        
        # Read all learned characters out from database
        new = self.db.dict_stats_new_characters_all_info()
        new_count = len(new)

        dlg.setWindowTitle(f"生字表（{new_count}）")

        # Fill table data from database
        table_data = []
        for record in new:
            table_data.append([record[0], record[1], record[2]])

        def configure_table(table_data_in, rows_in):
            # Configure the table
            table.clearContents()
            table.setRowCount(rows_in)
            table.setColumnCount(3)
            table.setHorizontalHeaderLabels(['生字', '使用次数', '覆盖率'])

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

            # 如果搜索框为空，则显示所有生字
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
        #table.setHorizontalHeaderLabels(['汉字','加入时间'])
        
        # Read all learned characters out from database
        learned = self.db.learned_all()
        learned_count = len(learned)

        dlg.setWindowTitle(f"识字表（{learned_count}）")

        # Fill table data from database
        table_data = []
        for record in learned:
            table_data.append([record[0], record[1]])

        def configure_table(table_data_in, rows_in):
            # Configure the table
            table.clearContents()
            table.setRowCount(rows_in)
            table.setColumnCount(2)
            table.setHorizontalHeaderLabels(['汉字','学习时间'])

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

            # 如果搜索框为空，则显示所有认识的汉字
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
        dlg.setWindowTitle("识字量分布图")
        dlg.resize(700, 500)

        layoutH = QHBoxLayout()
        layoutV = QVBoxLayout()

        # 从数据库中读取
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
        label_text += f"总识字量：{learned_total}"

        label_char = QLabel(dlg)
        label_char.setFont(QFont('楷体', 20))
        #label_char.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        label_char.resize(200, 200)
        label_char.setText(label_text)

        layoutH.addWidget(label_char)
        layoutH.addWidget(plot)

        dlg.setLayout(layoutH)
        dlg.exec()


    def onYesButtonClicked(self, s):
        # 当前汉字认识！
        text = self.characters[self.char_index]
        self.db.learned_insert_record(text, self.today)
        self.db.save()

        # 不需要访问数据库
        self.learned_count += 1

        # 找到下一个新字
        self.char_index += 1
        if self.char_index >= len(self.characters):
            text = "到达最后"
        else:
            text = self.characters[self.char_index]

        self.label_char.setText(text)
        self.label_learned.setText(f"[已认识： {self.learned_count}]")

    def onNoButtonClicked(self, s):
        # 找到下一个新字
        self.char_index += 1
        if self.char_index >= len(self.characters):
            text = "到达最后"
        else:
            text = self.characters[self.char_index]

        self.label_char.setText(text)

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()

