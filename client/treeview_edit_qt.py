# -*- coding: utf-8 -*-
"""Qt replacement for <File>treeview_edit.py</File>.

In the original Tkinter version, TreeviewEdit exists mainly to return the
selected item text on double-click. In Qt, QTableView already provides the
clicked index; this helper adds convenience methods.
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QTableView, QMessageBox


class ProjectTableView(QTableView):
    """A thin wrapper around QTableView.

    Emits projectActivated(str) when a row is double-clicked.
    """

    projectActivated = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.doubleClicked.connect(self._on_double_clicked)

    def selected_project_name(self) -> str:
        idx = self.currentIndex()
        if not idx.isValid():
            QMessageBox.warning(self, "No Project Selected", "Please select a project first.")
            return ""
        model = self.model()
        value = model.data(model.index(idx.row(), 0))
        return "" if value is None else str(value)

    def _on_double_clicked(self, index):
        if not index.isValid():
            return
        model = self.model()
        value = model.data(model.index(index.row(), 0))
        if value is None:
            return
        self.projectActivated.emit(str(value))
