# -*- coding: utf-8 -*-
from __future__ import annotations

import pathlib
import re
import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QToolBar, QInputDialog, QMessageBox, QFileDialog
from PySide6.QtGui import QAction

from .controller import SLDController
from .model import SLDModel
from .view import SLDView
from .Menu_Bar import SLDMenuBar
from .dialogs import AboutSLDDialog

from config.paths import CLIENT_DB
from config.paths import SLD_DB_ROOT


def safe_db_name(project_name: str) -> str:
    clean = re.sub(r"[^A-Za-z0-9_.-]+", "_", project_name.strip())
    clean = clean.strip("_")
    return clean or "unnamed_project"


def sld_db_path_for_project(project_name: str, root:
pathlib.Path = SLD_DB_ROOT) -> pathlib.Path:
    path = root / f"{safe_db_name(project_name)}_SLD.db"

    path.parent.mkdir(parents=True, exist_ok=True)
    return path


class SLDMainWindow(QMainWindow):
    def __init__(self, project: str = "", db_path: pathlib.Path | str | None = None, parent=None) -> None:
        super().__init__(parent)
        self.parent_window = parent

        if self.parent_window:
            self.project = project
            self.db_path = pathlib.Path(db_path) if db_path else sld_db_path_for_project(project)

            self.setWindowTitle("SLD Graph Editor (PySide MVC)")
            self.resize(980, 620)

            # db_path = PROJECT_ROOT / (f"{project}.db" if project else DB_ROOT.name)
            # Opened from the DB Client: the root's name follows the project name.
            self.model = SLDModel(self.db_path, self.project, sync_root_name=True)

            self.view = SLDView(self)
            try:
                self.controller = SLDController(self.model, self.view)
            except Exception:
                # Opening the database failed: don't leave a hidden, half-built
                # window attached to the DB Client.
                self.setParent(None)
                self.deleteLater()
                raise
            self.setCentralWidget(self.view)

            self.Menubar = SLDMenuBar()
            self.setMenuBar(self.Menubar)

            self.Menubar.newSLD_action.triggered.connect(self.new_SLD_clicked)
            self.Menubar.openSLD_action.triggered.connect(self.open_SLD_clicked)
            self.Menubar.exportSLD_action.triggered.connect(self.export_SLD_clicked)
            self.Menubar.exitSLD_action.triggered.connect(self.confirm_exit)
            self.Menubar.about_action.triggered.connect(self.about_project)

            self.statusBar().showMessage(f"Database: {self.db_path.name}{self._migration_note()}")

        else:
            QApplication.quit()

    def _migration_note(self) -> str:
        """Status-bar text telling the user an old-format file was converted."""
        result = self.model.last_migration
        if result is None:
            return ""
        note = f" (converted from the old SLD format; backup saved as {result.backup_path.name}"
        if result.unmatched_parents:
            note += f"; {len(result.unmatched_parents)} node(s) had an unknown parent and are now top-level"
        return note + ")"

    def closeEvent(self, event):
        # A window created without a parent has no model.
        close = getattr(getattr(self, "model", None), "close", None)
        if callable(close):
            close()
        if self.parent_window is not None:
            self.parent_window.show()
        super().closeEvent(event)

    def new_SLD_clicked(self):
        project, ok = QInputDialog.getText(
            None,
            "New SLD creation",
            "SLD database name:",
        )
        project = project.strip() if ok else ""
        if project == "":
            return
        self.db_path = sld_db_path_for_project(project)  # SLD_DB_ROOT / f"{project}.db"
        self.model = SLDModel(db_path=self.db_path, project_name=project)
        self.controller = SLDController(self.model, self.view)
        self.statusBar().showMessage(f"Created New Database: {self.db_path.name}{self._migration_note()}")
        # self.view.tree.setHeaderLabels([project])

    def open_SLD_clicked(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open SLD Project",
            str(SLD_DB_ROOT),  # starting directory
            "SLD Files (*.sld *.db);;All Files (*)"
        )

        if not file_path:
            return  # user cancelled

        try:
            # Initialize or reload model with selected DB
            # file_name = file_path.rsplit('/')[-1].split('.')
            file_name = pathlib.Path(file_path).stem
            self.model = SLDModel(file_path, file_name)

            # Reconnect controller + view if needed
            self.controller = SLDController(self.model, self.view)

            self.statusBar().showMessage(f"Opened Database: {file_path}{self._migration_note()}")

            # QMessageBox.information(self, "Success", f"Loaded: {file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def export_SLD_clicked(self):
        if not self.model:
            self.statusBar().showMessage(f"Cannot Export data if there is no open database!")
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export CSV",
            "raw_database.csv",
            "CSV files (.csv)"
        )

        if not file_path:
            return  # user cancelled
        else:
            self.model.export_database(file_path)
            print(f"Selected Folder: {file_path}")

    def confirm_exit(self):
        """Ask the user for confirmation before exiting."""
        reply = QMessageBox.question(
            self,
            "Confirm Exit",
            "Are you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.close()

    def about_project(self):
        """Open Dialog box with information about the project"""

        dialog = AboutSLDDialog(self)

        dialog.exec()


def main() -> int:
    app = QApplication(sys.argv)

    project = sys.argv[1] if len(sys.argv) > 1 else ""
    window = SLDMainWindow(project=project)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
