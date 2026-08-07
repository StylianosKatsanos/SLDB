
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from sld.model import RelationshipRow
from sld.view import SLDView

def get_app() -> QApplication:
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    return app

def test_set_detail_data_model() -> None:
    get_app()
    view = SLDView()

    rel = RelationshipRow("A", "Parent", "Type1")
    view.set_detail_data(rel)

    assert view.detail_model.rowCount() == 3
    assert view.detail_model.data(view.detail_model.index(2, 1), Qt.DisplayRole) == "Type1"