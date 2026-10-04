# -*- coding: utf-8 -*-
"""PyQt refactor of <File>DB_Client.py</File>.

Design goals:
- Preserve the original behaviors and flows from the Tkinter app.
- Replace Tk widgets with Qt widgets.
- Keep SQLite access via sqlite3, but improve safety by parameterizing queries.

Key preserved behaviors (as in the original):
- Reads Design Managers from Design_Managers on connect. 
- Reads headers from pragma_table_info and uses them for planned/actual dropdowns.
- Displays Projects in a single-column view (Project_Name). 
- Double-click shows a details dialog with a formatted key/value grid.
- Add Project, Modify Selected, Filter, Clear Filter, Open Path.
- Schedule export produces Project_Schedule.xlsx and launches Excel.
- Manager add/modify.

"""

import os
import webbrowser
from datetime import datetime

import pandas as pd

from sld.sld_main import SLDMainWindow

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QLabel, QGroupBox, QPushButton, QComboBox,
    QVBoxLayout, QHBoxLayout,
    QMessageBox, QDialog, QStyle,
    QSplitter, QTableView, QAbstractItemView, QSizePolicy,
    QToolButton
)

from .treeview_edit_qt import ProjectTableView
from .filter_window_qt import FilterWindowDialog, FilterSpec
from .repositories.repo import SQLiteRepo
from .dialogs.dialogs import (
    AddProjectDialog, AddManagerDialog,
    ModifyManagerDialog, ModifyProjectDialog, AboutClientDialog
)
from config.paths import CLIENT_DB

# Optional dependency from your existing project
try:
    from create_schedule import get_schedule
except Exception:
    get_schedule = None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Original defaults
        self.db_filename = CLIENT_DB
        self.table = 'Projects'
        self.filter_spec = FilterSpec()

        self.repo = SQLiteRepo(self.db_filename)
        self.headers = []
        self.desman = []

        self.setWindowTitle('Compliance Project Rollout')
        self.resize(800, 400)

        self._build_ui()
        self.on_connect()
        self.refresh_view()

    # ---------------- UI ----------------

    def _build_ui(self):
        root = QWidget(self)
        self.setCentralWidget(root)

        main = QVBoxLayout(root)

        #Message Area
        self.message = QLabel('')
        self.message.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.message.setMaximumHeight(50)
        self.message.setStyleSheet('color: red;')
        self.message.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)

        # Info Button
        top_row = QHBoxLayout()
        top_row.addWidget(self.message, 1)
        self.btn_info = QToolButton()
        self.btn_info.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation))
        self.btn_info.setToolTip('About this window')
        self.btn_info.setAutoRaise(True)
        top_row.addWidget(self.btn_info, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

        main.addLayout(top_row)

        # Data View
        gb_data = QGroupBox('Data View')
        gb_data_layout = QVBoxLayout(gb_data)

        # Splitter gives a draggable separator between the project list
        # and the inline details table.
        self.data_splitter = QSplitter(Qt.Orientation.Horizontal)

        self.view = ProjectTableView()
        self.data_splitter.addWidget(self.view)

        self.details_model = QStandardItemModel(0, 2, self)
        self.details_model.setHorizontalHeaderLabels(['Field', 'Value'])

        self.details_view = QTableView()
        self.details_view.setModel(self.details_model)
        self.details_view.setAlternatingRowColors(True)
        self.details_view.setWordWrap(False)
        self.details_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.details_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.details_view.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.details_view.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.details_view.horizontalHeader().setStretchLastSection(False)

        self.data_splitter.addWidget(self.details_view)
        self.data_splitter.setSizes([300, 760])
        gb_data_layout.addWidget(self.data_splitter)
        main.addWidget(gb_data)

        self.model = QStandardItemModel(0, 1, self)
        self.model.setHorizontalHeaderLabels(['Project_Name'])
        self.view.setModel(self.model)
        self.view.projectActivated.connect(self.on_project_activated)
        self.view.selectionModel().currentRowChanged.connect(self.on_project_selection_changed)

        # Buttons row (matching original set)
        btn_row1 = QHBoxLayout()
        self.btn_open_path = QPushButton('Open Path')
        self.btn_filter = QPushButton('Filter')
        self.btn_clear = QPushButton('Clear Filter')
        self.btn_add = QPushButton('Add New Entry')
        self.btn_modify = QPushButton('Modify Selected')
        btn_row1.addWidget(self.btn_open_path)
        btn_row1.addWidget(self.btn_filter)
        btn_row1.addWidget(self.btn_clear)
        btn_row1.addStretch(1)
        btn_row1.addWidget(self.btn_add)
        btn_row1.addWidget(self.btn_modify)
        main.addLayout(btn_row1)

        btn_row2 = QHBoxLayout()
        self.btn_open_sld = QPushButton('SLD Browser')
        btn_row2.addWidget(self.btn_open_sld)
        btn_row2.addStretch(1)
        main.addLayout(btn_row2)

        # Schedule
        gb_schedule = QGroupBox('Schedule')
        sch = QHBoxLayout(gb_schedule)
        self.btn_export = QPushButton('Export')
        self.cmb_year = QComboBox(); self.cmb_year.addItems([str(datetime.now().year), str(datetime.now().year+1)])
        sch.addWidget(self.btn_export)
        sch.addWidget(self.cmb_year)

        # Manager
        gb_manager = QGroupBox('Manager')
        man = QHBoxLayout(gb_manager)
        self.btn_add_man = QPushButton('Add Manager')
        self.btn_mod_man = QPushButton('Modify Manager')
        man.addWidget(self.btn_add_man)
        man.addWidget(self.btn_mod_man)

        lower = QHBoxLayout()
        lower.addWidget(gb_schedule)
        lower.addWidget(gb_manager)
        main.addLayout(lower)

        # Wire signals
        self.btn_open_path.clicked.connect(self.open_path)
        self.btn_filter.clicked.connect(self.open_filter)
        self.btn_clear.clicked.connect(self.clear_filter)
        self.btn_add.clicked.connect(self.add_project)
        self.btn_modify.clicked.connect(self.modify_project)
        self.btn_export.clicked.connect(self.export_schedule)
        self.btn_add_man.clicked.connect(self.add_manager)
        self.btn_mod_man.clicked.connect(self.modify_manager)
        self.btn_open_sld.clicked.connect(self.open_sld)
        self.btn_info.clicked.connect(self.open_about)

    # ---------------- Behaviors (mirror original) ----------------
    
    def check_db(func):
        def wrapper(self):
            if not self.db_filename:
                self.message.setText('No Database to refresh data')
                return
            func(self)
        return wrapper
    
    
    def on_connect(self):
        # Equivalent to on_connect_button_clicked (loads Design_Managers). 
        self.message.setText('')
        if not self.db_filename:
            self.message.setText('No database selected')
            return
        self.desman = [r[0] for r in self.repo.fetchall('SELECT * FROM Design_Managers')]

    @check_db
    def refresh_view(self):
        # headers from pragma_table_info
        self.headers = [r[0] for r in self.repo.fetchall(f'SELECT name FROM pragma_table_info("{self.table}");')]
        self.model.setHorizontalHeaderLabels([self.headers[0] if self.headers else 'Project_Name'])

        # view_entries equivalent
        self.model.removeRows(0, self.model.rowCount())
        self.clear_details()

        if not self.headers:
            self.message.setText(f'No columns found for table {self.table}')
            return

        query = f'SELECT * FROM {self.table} {self.filter_spec.where_sql} ORDER BY {self.headers[0]} COLLATE NOCASE desc;'
        rows = self.repo.fetchall(query, self.filter_spec.params)
        for row in rows:
            item = QStandardItem(str(row[0]))
            item.setEditable(False)
            self.model.insertRow(0, [item])

        if self.model.rowCount() > 0:
            self.view.selectRow(0)
            self.update_details_for_project(self.view.selected_project_name())

    def clear_details(self):
        self.details_model.removeRows(0, self.details_model.rowCount())
        self.details_model.setHorizontalHeaderLabels(['Field', 'Value'])

    def update_details_for_project(self, project_name: str):
        """Show the same field/value information as DetailsDialog inline."""
        self.clear_details()

        if str(self.table) != 'Projects':
            self.message.setText('Not applicable table for details view')
            return
        if not project_name:
            return
        if not self.headers:
            return

        row = self.repo.fetchall(f'SELECT * FROM {self.table} WHERE Project_Name=? ORDER BY ROWID;', (project_name,))
        if not row:
            self.message.setText('No data found')
            return

        for field, value in zip(self.headers, row[0]):
            field_item = QStandardItem(str(field))
            value_item = QStandardItem('' if value is None else str(value))
            field_item.setEditable(False)
            value_item.setEditable(False)
            self.details_model.appendRow([field_item, value_item])

        self.details_view.resizeColumnToContents(0)
        self.details_view.resizeColumnToContents(1)

    def on_project_selection_changed(self, current, previous):
        if not current.isValid():
            self.clear_details()
            return
        project_name = self.view.selected_project_name()
        self.update_details_for_project(project_name)

    def on_project_activated(self, project_name: str):
        # Double-click now refreshes the inline details table instead of opening a dialog.
        self.message.setText('')
        self.update_details_for_project(project_name)

    def open_path(self):
        self.message.setText('')
        if self.table != 'Projects':
            return
        project_name = self.view.selected_project_name()
        if not project_name:
            self.message.setText('No Entry to open server path from')
            return
        res = self.repo.fetchall(f'SELECT Server_Path FROM {self.table} WHERE Project_Name=?', (project_name,))
        if not res:
            self.message.setText('No Server_Path found')
            return
        webbrowser.open(str(res[0][0]))
        self.message.setText('URL opened')

    def open_filter(self):
        self.message.setText('')
        if not self.table:
            self.message.setText('Please select a database or a table to filter data')
            return

        # Original passes headers[5:] and desman
        dlg = FilterWindowDialog(date_columns=self.headers[5:], design_managers=self.desman, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.filter_spec = dlg.result()
            self.message.setText('Filter Created')
            self.refresh_view()

    def clear_filter(self):
        self.message.setText('')
        self.filter_spec = FilterSpec()
        self.message.setText('Filter Cleared')
        self.refresh_view()

    def add_project(self):
        self.message.setText('')
        if not self.table:
            self.message.setText('No database to add entry')
            return
        if self.table != 'Projects':
            return

        dlg = AddProjectDialog(self.desman, self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        name = dlg.edt_name.text().strip()
        if not name:
            self.message.setText('You have to enter a name to insert an new entry.')
            return

        # Preserve original insert: (?,?,?,?,?, NULL...)
        nulls = max(len(self.headers) - 6, 0)
        query = 'INSERT INTO Projects VALUES(?,?,?,?,?,' + (nulls * 'NULL,') + 'NULL)'
        params = tuple(None if v == '' else v for v in (
            name,
            dlg.edt_code.text().strip(),
            dlg.cmb_manager.currentText().strip(),
            dlg.cmb_status.currentText().strip(),
            dlg.edt_path.text().strip(),
        ))
        self.repo.execute(query, params)
        self.message.setText(f'New Entry with name {name} added')
        self.on_connect()
        self.refresh_view()

    def modify_project(self):
        self.message.setText('')
        if str(self.table) != 'Projects':
            return
        project_name = self.view.selected_project_name()
        if not project_name:
            self.message.setText('No item selected to modify')
            return

        dlg = ModifyProjectDialog(project_name, self.headers, self.desman, self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        # Mirror update_entries precedence: status -> manager -> code -> path -> dates
        if dlg.chk_status.isChecked():
            self.repo.execute(f'UPDATE {self.table} SET Status=? WHERE Project_Name=?', (dlg.cmb_status.currentText(), project_name))

        elif dlg.chk_manager.isChecked():
            self.repo.execute(f'UPDATE {self.table} SET Design_Manager=? WHERE Project_Name=?', (dlg.cmb_manager.currentText(), project_name))

        elif dlg.chk_code.isChecked():
            self.repo.execute(f'UPDATE {self.table} SET Project_Code=? WHERE Project_Name=?', (dlg.edt_code.text(), project_name))

        elif dlg.chk_path.isChecked():
            self.repo.execute(f'UPDATE {self.table} SET Server_Path=? WHERE Project_Name=?', (dlg.edt_path.text(), project_name))

        else:
            plan_col = dlg.cmb_plan_col.currentText()
            act_col = dlg.cmb_act_col.currentText()
            param = plan_col if plan_col != '' else act_col
            if param == '':
                return

            if dlg.chk_revision.isChecked():
                # append revision using SQLite concatenation, like the original
                value = 'N/A' if dlg.chk_na.isChecked() else (
                    dlg.dt_plan.date().toString('yyyy-MM-dd') if plan_col else dlg.dt_act.date().toString('yyyy-MM-dd')
                )
                self.repo.execute(f'UPDATE {self.table} SET [{param}] = [{param}] || "->" || ? WHERE Project_Name=?', (value, project_name))
            else:
                value = 'N/A' if dlg.chk_na.isChecked() else (
                    dlg.dt_plan.date().toString('yyyy-MM-dd') if plan_col else dlg.dt_act.date().toString('yyyy-MM-dd')
                )
                self.repo.execute(f'UPDATE {self.table} SET [{param}] = ? WHERE Project_Name=?', (value, project_name))

        self.message.setText(f'Entry {project_name} modified')
        self.refresh_view()

    def add_manager(self):
        dlg = AddManagerDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        name = dlg.edt_name.text().strip()
        if not name:
            self.message.setText('No name inserted')
            return
        self.repo.execute('INSERT INTO Design_Managers VALUES(?)', (name,))
        self.on_connect()
        self.message.setText('New manager added')
        self.refresh_view()

    def modify_manager(self):
        dlg = ModifyManagerDialog(self.desman, self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        old = dlg.cmb_old.currentText().strip()
        new = dlg.edt_new.text().strip()
        if not old or not new:
            self.message.setText('No name inserted')
            return
        self.repo.execute('UPDATE Design_Managers SET Manager_Name=? WHERE Manager_Name=?', (new, old))
        self.on_connect()
        self.message.setText('Manager modified')
        self.refresh_view()

    def export_schedule(self):
        self.message.setText('')
        if self.model.rowCount() == 0:
            self.message.setText('No connected database/table')
            return
        if self.cmb_year.currentText() == '':
            self.message.setText('No Schedule Year selected')
            return
        if get_schedule is None:
            QMessageBox.warning(self, 'Missing dependency', 'create_schedule.get_schedule is not available')
            return

        sch_table = get_schedule(self.cmb_year.currentText(), self.db_filename)
        writer = pd.ExcelWriter('Project_Schedule.xlsx', engine='xlsxwriter')
        sch_table.to_excel(writer, sheet_name='Schedule', startrow=1, header=False)
        workbook = writer.book
        worksheet = writer.sheets['Schedule']

        total_format = workbook.add_format({'text_wrap': True, 'valign': 'top'})
        for i in range(0, 15):
            worksheet.set_column(i, 1, 25, total_format)

        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1,
        })

        week = datetime.now().strftime('%W/%Y')
        worksheet.write(0, 0, week)
        for col_num, value in enumerate(sch_table.columns.values):
            worksheet.write(0, col_num + 1, value, header_format)
        worksheet.freeze_panes(1, 1)
        writer.close()

        os.system('start "EXCEL.exe" {}'.format('Project_Schedule.xlsx'))

    def open_sld(self):
        project_name = self.view.selected_project_name()
        if not project_name:
            self.message.setText('Select a project first to open its SLD')
            return
        
        if not hasattr(self, "_sld_windows"):
            self._sld_windows = {}
            
        existing = self._sld_windows.get(project_name)
        if existing is not None:
            existing.raise_()
            existing.activateWindow()
            return
     
        window = SLDMainWindow(project=project_name, parent=self)
        window.destroyed.connect(lambda *_args, 
                                 name=project_name: self._sld_windows.pop(name, None))
        
        self._sld_windows[project_name] = window
        window.show()

    def open_about(self):

        dialog = AboutClientDialog(self)

        dialog.exec()

def main():
    import sys
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
