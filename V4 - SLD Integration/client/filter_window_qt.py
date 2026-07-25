# -*- coding: utf-8 -*-
"""
"""

from dataclasses import dataclass
from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox, QCheckBox,
    QDateEdit, QLabel, QPushButton, QHBoxLayout, QVBoxLayout
)


@dataclass(frozen=True)
class FilterSpec:
    where_sql: str = ""      # e.g. 'WHERE Project_Name LIKE ? AND Status = ?'
    params: tuple = tuple()  # parameters bound to sqlite


class FilterWindowDialog(QDialog):
    """Filter builder dialog.

    Note: because we don't have full original Tkinter filter UI here, this is a
    faithful *minimal* filter set that matches the fields your main client uses:
    - Project_Name (LIKE)
    - Design_Manager (equals)
    - Status (equals)
    - Optional date range on a chosen column

    You can easily extend this later to match the full Tk filter UI.
    """

    def __init__(self, date_columns=(), design_managers=(), parent=None):
        super().__init__(parent)
        self.setWindowTitle('Filter')
        self._result = FilterSpec()

        # controls
        self.chk_name = QCheckBox('Project Name contains')
        self.edt_name = QLineEdit()

        self.chk_manager = QCheckBox('Design Manager is')
        self.cmb_manager = QComboBox(); self.cmb_manager.addItems([''] + list(design_managers))

        self.chk_status = QCheckBox('Status is')
        self.cmb_status = QComboBox(); self.cmb_status.addItems(['', 'PRELIMINARY', 'IFR', 'IFC', 'AS-BUILT', 'CLOSED'])

        self.chk_date = QCheckBox('Date column between')
        self.cmb_date_col = QComboBox(); self.cmb_date_col.addItems([''] + list(date_columns))

        self.dt_from = QDateEdit(); self.dt_from.setCalendarPopup(True)
        self.dt_from.setDisplayFormat('yyyy-MM-dd')
        self.dt_from.setDate(QDate.currentDate().addMonths(-1))

        self.dt_to = QDateEdit(); self.dt_to.setCalendarPopup(True)
        self.dt_to.setDisplayFormat('yyyy-MM-dd')
        self.dt_to.setDate(QDate.currentDate())

        # preview
        self.preview = QLabel('')
        self.preview.setWordWrap(True)
        self.preview.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        # layout
        root = QVBoxLayout(self)
        form = QFormLayout()
        form.addRow(self.chk_name, self.edt_name)
        form.addRow(self.chk_manager, self.cmb_manager)
        form.addRow(self.chk_status, self.cmb_status)
        form.addRow(self.chk_date, self.cmb_date_col)
        form.addRow('From:', self.dt_from)
        form.addRow('To:', self.dt_to)
        root.addLayout(form)
        root.addWidget(QLabel('Preview (WHERE clause):'))
        root.addWidget(self.preview)

        btns = QHBoxLayout()
        btn_apply = QPushButton('Apply')
        btn_cancel = QPushButton('Cancel')
        btn_apply.clicked.connect(self._apply)
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(btn_apply)
        btns.addWidget(btn_cancel)
        root.addLayout(btns)

    def _apply(self):
        clauses = []
        params = []

        if self.chk_name.isChecked() and self.edt_name.text().strip():
            clauses.append('Project_Name LIKE ?')
            params.append(f"%{self.edt_name.text().strip()}%")

        if self.chk_manager.isChecked() and self.cmb_manager.currentText().strip():
            clauses.append('Design_Manager = ?')
            params.append(self.cmb_manager.currentText().strip())

        if self.chk_status.isChecked() and self.cmb_status.currentText().strip():
            clauses.append('Status = ?')
            params.append(self.cmb_status.currentText().strip())

        if self.chk_date.isChecked() and self.cmb_date_col.currentText().strip():
            col = self.cmb_date_col.currentText().strip()
            clauses.append(f'[{col}] BETWEEN ? AND ?')
            params.append(self.dt_from.date().toString('yyyy-MM-dd'))
            params.append(self.dt_to.date().toString('yyyy-MM-dd'))

        where_sql = ''
        if clauses:
            where_sql = 'WHERE ' + ' AND '.join(clauses)

        self._result = FilterSpec(where_sql=where_sql, params=tuple(params))
        self.preview.setText(where_sql)
        self.accept()

    def result(self) -> FilterSpec:
        return self._result
