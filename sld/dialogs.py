
# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import (
    QDialog, 
    QDialogButtonBox, 
    QFormLayout, 
    QLineEdit, 
    QWidget, 
    QCheckBox, 
    QSpinBox, 
    QComboBox,
    QVBoxLayout,
    QLabel,
    QPushButton
)

from PySide6.QtCore import Qt
from .types_config import TYPES
from .model import RelationshipRow


class NodeDialog(QDialog):
    def __init__(self, parent: Optional[QWidget] = None, *, title: str = "Node", data: Optional[RelationshipRow] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        
        # Existing fields
        self.name_edit = QLineEdit()
        self.parent_edit = QLineEdit()
        self.type_combo = QComboBox()
        self._populate_type_combo()

        
        # New checkbox
        self.multiple_checkbox = QCheckBox("multiple inputs")
        
        # New spinbox (positive integers only)
        self.number_spin = QSpinBox()
        self.number_spin.setMinimum(1)
        self.number_spin.setMaximum(100)  # optional upper bound

        # Disabled initially
        self.number_spin.setEnabled(False)
        
        if data:
            self.name_edit.setText(data.entry_name)
            self.parent_edit.setText(data.attached_to)
            self._set_type(data.entry_type)
            
        # Layout
        form = QFormLayout(self)
        form.addRow("Entry Name", self.name_edit)
        form.addRow("Attached To", self.parent_edit)
        form.addRow("Type", self.type_combo)
        
        # Multiple Checkbox
        form.addRow(self.multiple_checkbox)
        
        # Number Row (initially hidden)
        self.number_row_label = "Number"
        form.addRow(self.number_row_label, self.number_spin)
        

        # Connect signal
        self.multiple_checkbox.stateChanged.connect(self._toggle_multiple)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)


    def _toggle_multiple(self, state: int):
        is_checked = self.multiple_checkbox.isChecked()
        self.number_spin.setEnabled(is_checked)
        if is_checked:
            self.number_spin.setValue(1)
        
        label = self.layout().labelForField(self.number_spin)
        if label:
            label.setEnabled(is_checked)
        
        # Optional: resize dialog automatically
        self.adjustSize()
        
    
    def _populate_type_combo(self):
            for category, items in TYPES.items():
                # Disabled category header
                self.type_combo.addItem(f"--- {category} ---")
                index = self.type_combo.count() - 1
                self.type_combo.model().item(index).setEnabled(False)

                for item in items:
                    self.type_combo.addItem(item)
                    
    
    def _set_type(self, value: str):
            index = self.type_combo.findText(value)
            if index >= 0:
                self.type_combo.setCurrentIndex(index)
        
    
    def get_payload(self) -> dict:
        return {
            "entry_name":self.name_edit.text().strip(),
            "attached_to":self.parent_edit.text().strip(),
            "entry_type":self.type_combo.currentText().strip() or None,
            "is_multiple":self.multiple_checkbox.isChecked(),
            "multiple_count": self.number_spin.value(),
            }
    
    def get_data(self) -> RelationshipRow:
        payload = self.get_payload()
        rel = RelationshipRow(
            entry_name=payload["entry_name"],
            attached_to=payload["attached_to"],
            entry_type=payload["entry_type"]
        )
        
        return rel


class AboutSLDDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("About SLD Tool")
        self.setMinimumWidth(300)

        layout = QVBoxLayout(self)

        title = QLabel("<h2>SLD Tool v1.0</h2>")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        author = QLabel("<b>Created by:</b> Stylianos Katsanos")
        author.setAlignment(Qt.AlignmentFlag.AlignCenter)

        description = QLabel("Data Storage tool for Single Line Diagrams")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)

        link = QLabel('<a href="https://github.com/stylianoskatsanos">GitHub Repository</a>')
        link.setAlignment(Qt.AlignmentFlag.AlignCenter)
        link.setOpenExternalLinks(True)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)

        layout.addWidget(title)
        layout.addWidget(author)
        layout.addWidget(description)
        layout.addWidget(link)
        layout.addWidget(close_btn)
        
        