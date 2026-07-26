# -*- coding: utf-8 -*-
"""
Created on Sat Jun 20 15:55:12 2026

@author: stkats
"""

# -*- coding: utf-8 -*-
from PySide6.QtWidgets import (
    QMenu,
    QMenuBar
)

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction

from .detail_table_model import DetailTableModel
from .dialogs import NodeDialog
from .model import RelationshipRow


"""QMenuBar for file access: no DB Logic"""
class SLDMenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        file_menu = QMenu("File", self)
        help_menu = QMenu("Help", self)
        self.addMenu(file_menu)
        self.addMenu(help_menu)
        file_menu.addSeparator()
        
        #### ------------------ File Button ---------------------- ####
        
        # ---------------- Create new SLD ----------------------------#
        self.newSLD_action = QAction("New", self)
        self.newSLD_action.setStatusTip("Create a new SLD File")
        self.newSLD_action.setShortcut("Ctrl+N")  # Keyboard shortcut
        
        # --------------- Open existing SLD --------------------------#
        self.openSLD_action = QAction("Open", self)
        self.openSLD_action.setStatusTip("Open an existing SLD File")
        self.openSLD_action.setShortcut("Ctrl+O")  # Keyboard shortcut
        
        # --------------- Export existing SLD --------------------------#
        self.exportSLD_action = QAction("Export", self)
        self.exportSLD_action.setStatusTip("Export an existing SLD File")
        self.exportSLD_action.setShortcut("Ctrl+E")  # Keyboard shortcut
        
        # --------------- Exit Viewer --------------------------------#
        
        self.exitSLD_action = QAction("Exit", self)
        self.exitSLD_action.setStatusTip("Exit Program")
        self.exitSLD_action.setShortcut("Ctrl+Q")  # Keyboard shortcut
        
        #### ------------------ Help Button ---------------------- ####
        
        self.about_action = QAction("About", self)
        self.about_action.setStatusTip("About Program")
        
        file_menu.addAction(self.newSLD_action)
        file_menu.addAction(self.openSLD_action)
        file_menu.addAction(self.exportSLD_action)
        file_menu.addAction(self.exitSLD_action)
        help_menu.addAction(self.about_action)
    
    
    


