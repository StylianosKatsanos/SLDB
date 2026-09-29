# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 21:47:35 2026

@author: stkats
"""

from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QLabel, QGroupBox, QPushButton, QComboBox,
    QVBoxLayout, QHBoxLayout,
    QMessageBox, QDialog, QFormLayout, QLineEdit, QCheckBox, QDateEdit,
    QSplitter, QTableView, QAbstractItemView, QSizePolicy
)

class DetailsDialog(QDialog):
    def __init__(self, headers, row, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Project Details')

        layout = QVBoxLayout(self)
        title = QLabel('Project Details')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        from PySide6.QtWidgets import QTextEdit
        txt = QTextEdit(self)
        txt.setReadOnly(True)
        res = list(zip(headers, row))
        #txt.setPlainText(tabulate(res, tablefmt='grid', stralign=('center',)))
        layout.addWidget(txt)

        btn = QPushButton('Close')
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

        self.resize(900, 500)


class AddProjectDialog(QDialog):
    def __init__(self, desman, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Insert New Entry')

        self.edt_name = QLineEdit()
        self.edt_code = QLineEdit()
        self.cmb_manager = QComboBox(); self.cmb_manager.addItems(list(desman))
        self.cmb_status = QComboBox(); self.cmb_status.addItems(['PRELIMINARY', 'IFR', 'IFC', 'AS-BUILT', 'CLOSED'])
        self.edt_path = QLineEdit()

        form = QFormLayout(self)
        form.addRow('Project Name:', self.edt_name)
        form.addRow('Project Code:', self.edt_code)
        form.addRow('Design Manager:', self.cmb_manager)
        form.addRow('Status:', self.cmb_status)
        form.addRow('Server Path:', self.edt_path)

        btn_row = QHBoxLayout()
        ok = QPushButton('Insert Entry')
        cancel = QPushButton('Cancel')
        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        btn_row.addWidget(ok); btn_row.addWidget(cancel)
        form.addRow(btn_row)


class AddManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Insert New Design Manager')
        self.edt_name = QLineEdit()
        form = QFormLayout(self)
        form.addRow('Manager Name:', self.edt_name)
        btn_row = QHBoxLayout()
        ok = QPushButton('Insert Manager'); cancel = QPushButton('Cancel')
        ok.clicked.connect(self.accept); cancel.clicked.connect(self.reject)
        btn_row.addWidget(ok); btn_row.addWidget(cancel)
        form.addRow(btn_row)


class ModifyManagerDialog(QDialog):
    def __init__(self, desman, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Update Manager')
        self.cmb_old = QComboBox(); self.cmb_old.addItems(list(desman))
        self.edt_new = QLineEdit()
        form = QFormLayout(self)
        form.addRow('Old Manager Name:', self.cmb_old)
        form.addRow('New Manager Name:', self.edt_new)
        btn_row = QHBoxLayout()
        ok = QPushButton('Update'); cancel = QPushButton('Cancel')
        ok.clicked.connect(self.accept); cancel.clicked.connect(self.reject)
        btn_row.addWidget(ok); btn_row.addWidget(cancel)
        form.addRow(btn_row)


class ModifyProjectDialog(QDialog):
    """Qt version of open_modify_window() + disable_plan/disable_act behavior."""

    def __init__(self, project_name: str, headers, desman, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Update Entry')

        self.project_name = project_name

        self.chk_status = QCheckBox('Only Change Status')
        self.cmb_status = QComboBox(); self.cmb_status.addItems(['PRELIMINARY', 'IFR', 'IFC', 'AS-BUILT', 'CLOSED'])

        self.chk_manager = QCheckBox('Only Change Manager')
        self.cmb_manager = QComboBox(); self.cmb_manager.addItems(list(desman))

        self.chk_code = QCheckBox('Only Change Project Code')
        self.edt_code = QLineEdit()

        self.chk_path = QCheckBox('Only Change Project Path')
        self.edt_path = QLineEdit()

        self.chk_revision = QCheckBox('Add Revision')
        self.chk_na = QCheckBox('Add N/A')

        excluded = {'Status', 'Design_Manager', 'Project_Code', 'Server_Path'}
        planned_cols = [''] + [x for x in headers[1::2] if x not in excluded]
        actual_cols = [''] + [x for x in headers[2::2] if x not in excluded]

        self.cmb_plan_col = QComboBox(); self.cmb_plan_col.addItems(planned_cols)
        self.cmb_act_col = QComboBox(); self.cmb_act_col.addItems(actual_cols)

        self.dt_plan = QDateEdit(); self.dt_plan.setCalendarPopup(True)
        self.dt_plan.setDisplayFormat('yyyy-MM-dd'); self.dt_plan.setDate(QDate.currentDate())

        self.dt_act = QDateEdit(); self.dt_act.setCalendarPopup(True)
        self.dt_act.setDisplayFormat('yyyy-MM-dd'); self.dt_act.setDate(QDate.currentDate())

        self.cmb_plan_col.currentTextChanged.connect(self._disable_act)
        self.cmb_act_col.currentTextChanged.connect(self._disable_plan)

        form = QFormLayout(self)
        form.addRow('Project:', QLabel(project_name))
        form.addRow(self.chk_status, self.cmb_status)
        form.addRow(self.chk_manager, self.cmb_manager)
        form.addRow(self.chk_code, self.edt_code)
        form.addRow(self.chk_path, self.edt_path)
        form.addRow(self.chk_revision, self.chk_na)
        form.addRow('Planned:', self.cmb_plan_col)
        form.addRow('Planned date:', self.dt_plan)
        form.addRow('Actual:', self.cmb_act_col)
        form.addRow('Actual date:', self.dt_act)

        btn_row = QHBoxLayout()
        ok = QPushButton('Update Entry'); cancel = QPushButton('Cancel')
        ok.clicked.connect(self.accept); cancel.clicked.connect(self.reject)
        btn_row.addWidget(ok); btn_row.addWidget(cancel)
        form.addRow(btn_row)

    def _disable_act(self, _):
        self.cmb_act_col.setEnabled(self.cmb_plan_col.currentText() == '')

    def _disable_plan(self, _):
        self.cmb_plan_col.setEnabled(self.cmb_act_col.currentText() == '')

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("About SLD Tool")
        self.setMinimumWidth(300)

        layout = QVBoxLayout(self)

        title = QLabel("<h2>SLD Tool v1.0</h2>")
        title.setAlignment(Qt.AlignCenter)

        author = QLabel("<b>Created by:</b> Stylianos Katsanos")
        author.setAlignment(Qt.AlignCenter)

        description = QLabel("Data Storage tool for Single Line Diagrams")
        description.setAlignment(Qt.AlignCenter)

        link = QLabel('<a href="https://github.com/stylianoskatsanos">GitHub Repository</a>')
        link.setAlignment(Qt.AlignCenter)
        link.setOpenExternalLinks(True)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)

        layout.addWidget(title)
        layout.addWidget(author)
        layout.addWidget(description)
        layout.addWidget(link)
        layout.addWidget(close_btn)
