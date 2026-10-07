# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 17:21:47 2026

@author: stkats
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QStyledItemDelegate, QComboBox
from .types_config import TYPES


class TypeComboDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        # Only apply to specific cell
        if not self._use_combo(index):
            return super().createEditor(parent, option, index)

        combo = QComboBox(parent)

        for category, items in TYPES.items():
            combo.addItem(f"--- {category} ---")
            header_index = combo.count() - 1
            combo.model().item(header_index).setEnabled(False)

            for item in items:
                combo.addItem(item)

        return combo

    def setEditorData(self, editor, index):
        if isinstance(editor, QComboBox):
            value = index.model().data(index, Qt.EditRole)
            i = editor.findText(value)
            if i >= 0:
                editor.setCurrentIndex(i)
            else:
                editor.setCurrentIndex(-1) # show no selection if current value not in TYPES
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        if isinstance(editor, QComboBox):
            value = editor.currentText()

            if not value or value.startswith("---"):
                return

            model.setData(index, value, Qt.EditRole)
        else:
            super().setModelData(editor, model, index)
            
    def updatedEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    # Control WHERE the combobox appears
    def _use_combo(self, index):
        
        if index.column() != 1:
            return False
        
        field_index = index.sibling(index.row(), 0) 
        field_name = index.model().data(field_index, Qt.DisplayRole)
        
        return field_name == "Type"
