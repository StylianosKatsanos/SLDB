
# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal

from .model import RelationshipRow


class DetailTableModel(QAbstractTableModel):
    """Editable 2-column model for node details."""

    value_changed = Signal(str, str)

    HEADERS = ("Field", "Value")
    FIELD_ENTRY_NAME = "Entry Name"
    FIELD_ATTACHED_TO = "Attached To"
    FIELD_TYPE = "Type"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._rows: List[Tuple[str, str]] = []
        self._suppress_change_signal = False

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._rows)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return 2

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._rows)):
            return None
        field_name, value = self._rows[index.row()]
        if role in (Qt.DisplayRole, Qt.EditRole):
            return field_name if index.column() == 0 else value
        return None

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole) -> bool:
        if role != Qt.EditRole or not index.isValid() or index.column() != 1:
            return False
        row = index.row()
        if not (0 <= row < len(self._rows)):
            return False

        field_name, old_value = self._rows[row]
        new_value = "" if value is None else str(value)
        if new_value == old_value:
            return False

        self._rows[row] = (field_name, new_value)
        self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])

        if not self._suppress_change_signal:
            self.value_changed.emit(field_name, new_value)
        return True

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.NoItemFlags
        base = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        if index.column() == 1:
            base |= Qt.ItemIsEditable
        return base

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal and 0 <= section < len(self.HEADERS):
            return self.HEADERS[section]
        return None

    def set_relationship(self, rel: Optional[RelationshipRow]) -> None:
        rows: Sequence[Tuple[str, str]]
        if rel is None:
            rows = []
        else:
            rows = [
                (self.FIELD_ENTRY_NAME, rel.entry_name),
                (self.FIELD_ATTACHED_TO, rel.attached_to),
                (self.FIELD_TYPE, rel.entry_type or ""),
            ]

        self.beginResetModel()
        self._suppress_change_signal = True
        self._rows = list(rows)
        self._suppress_change_signal = False
        self.endResetModel()

    def relationship_field_value(self, field_name: str) -> Optional[str]:
        for row_field, row_value in self._rows:
            if row_field == field_name:
                return row_value
        return None
