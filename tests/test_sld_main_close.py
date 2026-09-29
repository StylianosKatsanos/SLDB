import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox

from sld.sld_main import SLDMainWindow

def get_app() -> QApplication:
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    return app

def make_window(tmp_path, parent=None) -> SLDMainWindow:
    # Use a temporary database so the tests never touch ClientDatabase/.
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

def test_close_without_parent_does_not_fail(tmp_path) -> None:
    get_app()
    window = make_window(tmp_path)

    window.show()
    window.close()

    assert not window.isVisible()

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