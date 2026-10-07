import sqlite3
import sys

import pytest
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox

from sld.schema import LegacySchemaError
from sld.sld_main import SLDMainWindow

def get_app() -> QApplication:
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    return app

def make_window(tmp_path, parent=None) -> SLDMainWindow:
    # The SLD window is only built when opened from the DB Client, so every
    # test gives it a parent window. A temporary database keeps
    # ClientDatabase/ untouched.
    parent = parent or QMainWindow()
    return SLDMainWindow(project="Test", db_path=tmp_path / "test_SLD.db", parent=parent)

def test_close_calls_model_close(tmp_path, monkeypatch) -> None:
    get_app()
    window = make_window(tmp_path)
    calls = []
    monkeypatch.setattr(window.model, "close", lambda: calls.append("closed"))

    window.show()
    window.close()

    assert calls == ["closed"]

def test_close_shows_parent_window(tmp_path) -> None:
    get_app()
    parent = QMainWindow()
    parent.hide()
    window = make_window(tmp_path, parent=parent)

    window.show()
    window.close()

    assert parent.isVisible()

def test_confirm_exit_yes_closes_window(tmp_path, monkeypatch) -> None:
    get_app()
    window = make_window(tmp_path)
    monkeypatch.setattr(QMessageBox, "question", lambda *args, **kwargs: QMessageBox.Yes)

    window.show()
    window.confirm_exit()

    assert not window.isVisible()

def test_confirm_exit_no_keeps_window_open(tmp_path, monkeypatch) -> None:
    get_app()
    window = make_window(tmp_path)
    calls = []
    monkeypatch.setattr(window.model, "close", lambda: calls.append("closed"))
    monkeypatch.setattr(QMessageBox, "question", lambda *args, **kwargs: QMessageBox.No)

    window.show()
    window.confirm_exit()

    assert window.isVisible()
    assert calls == []

def test_close_without_parent_does_not_fail(tmp_path) -> None:
    # Without a parent the window is not built (no model); closing it must still work.
    get_app()
    window = SLDMainWindow(project="Test", db_path=tmp_path / "test_SLD.db")

    window.show()
    window.close()

    assert not window.isVisible()

def test_failed_open_leaves_no_window_behind(tmp_path) -> None:
    get_app()
    db_path = tmp_path / "broken_SLD.db"
    with sqlite3.connect(db_path) as conn:
        # Old-format file with a nameless node: the migration refuses it.
        conn.execute("CREATE TABLE Relationships (Entry_name TEXT PRIMARY KEY, Attached_to TEXT, Type TEXT)")
        conn.execute("INSERT INTO Relationships VALUES (NULL, 'Test', 'Plot')")
    parent = QMainWindow()

    with pytest.raises(LegacySchemaError):
        SLDMainWindow(project="Test", db_path=db_path, parent=parent)

    assert parent.findChildren(SLDMainWindow) == []
