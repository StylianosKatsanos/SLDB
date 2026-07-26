
# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QHeaderView,
    QMenu,
    QMessageBox,
    QSplitter,
    QTableView,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from PySide6.QtGui import QAction

from .detail_table_model import DetailTableModel
from .dialogs import NodeDialog
from .model import RelationshipRow
from .delegates import TypeComboDelegate


class SLDView(QWidget):
    """UI only: no DB logic here."""

    add_requested = Signal()
    edit_requested =Signal()
    delete_requested = Signal()
    selection_changed = Signal()
    detail_value_changed = Signal(str, str)

    FIELD_ENTRY_NAME = DetailTableModel.FIELD_ENTRY_NAME
    FIELD_ATTACHED_TO = DetailTableModel.FIELD_ATTACHED_TO
    FIELD_TYPE = DetailTableModel.FIELD_TYPE

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.current_entry_name: Optional[str] = None

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["SLD Structure"])
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._show_tree_context_menu)
        self.tree.itemSelectionChanged.connect(self.selection_changed.emit)

        self.table = QTableView()
        self.detail_model = DetailTableModel(self)
        self.table.setModel(self.detail_model)
        self.table.setItemDelegate(TypeComboDelegate(self.table))
        
        self.detail_model.value_changed.connect(self.detail_value_changed.emit)
        self.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(
            QAbstractItemView.DoubleClicked
            | QAbstractItemView.EditKeyPressed
            | QAbstractItemView.SelectedClicked
        )
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.resizeRowsToContents()

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.tree)
        splitter.addWidget(self.table)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)

        layout = QVBoxLayout(self)
        layout.addWidget(splitter)

        self.action_add = QAction("Add Node", self)
        self.action_edit = QAction("Edit Node", self)
        self.action_delete = QAction("Delete Node", self)
        self.action_add.triggered.connect(self.add_requested.emit)
        self.action_edit.triggered.connect(self.edit_requested.emit)
        self.action_delete.triggered.connect(self.delete_requested.emit)

    def _show_tree_context_menu(self, pos) -> None:
        menu = QMenu(self)
        menu.addAction(self.action_add)
        if self.selected_entry_name() is not None:
            menu.addAction(self.action_edit)
            menu.addAction(self.action_delete)
        menu.exec_(self.tree.viewport().mapToGlobal(pos))

    def clear_tree(self) -> None:
        self.tree.clear()

    def add_tree_item(self, parent_item: Optional[QTreeWidgetItem], rel: RelationshipRow) -> QTreeWidgetItem:
        item = QTreeWidgetItem([rel.entry_name])
        item.setData(0, Qt.UserRole, rel.entry_name)
        item.setData(0, Qt.UserRole + 1, rel.attached_to)
        item.setData(0, Qt.UserRole + 2, rel.entry_type or "")
        if parent_item is None:
            self.tree.addTopLevelItem(item)
        else:
            parent_item.addChild(item)
        return item

    def expand_all(self) -> None:
        self.tree.expandAll()

    def selected_entry_name(self) -> Optional[str]: 
        item = self.current_tree_item()
        if item is None:
            return None
        return item.data(0, Qt.UserRole)

    def current_tree_item(self) -> Optional[QTreeWidgetItem]:
        items = self.tree.selectedItems()
        return items[0] if items else None

    def select_entry(self, entry_name: str) -> bool:
        matches = self.tree.findItems(entry_name, Qt.MatchRecursive | Qt.MatchExactly, 0)
        if not matches:
            return False
        self.tree.setCurrentItem(matches[0])
        return True

    def set_detail_data(self, rel: Optional[RelationshipRow]) -> None:
        self.current_entry_name = rel.entry_name if rel is not None else None
        self.detail_model.set_relationship(rel)

    def show_error(self, title: str, message: str) -> None:
        QMessageBox.critical(self, title, message)

    def show_warning(self, title: str, message: str) -> None:
        QMessageBox.warning(self, title, message)

    def ask_delete_confirmation(self, entry_name: str) -> bool:
        msg = QMessageBox(self)
        msg.setWindowTitle("Delete node")
        msg.setIcon(QMessageBox.Warning)
        msg.setText(f"Delete '{entry_name}'?")
        msg.setInformativeText("Children will be reattached to the deleted node's parent.")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        return msg.exec_() == QMessageBox.Yes

    def open_node_dialog(self, *, title: str, data: Optional[RelationshipRow] = None) -> Optional[RelationshipRow]:
        dialog = NodeDialog(self, title=title, data=data)
        if dialog.exec_() == QDialog.Accepted:
            return dialog.get_payload()
        return None
