
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from model import RelationshipRow
from view import SLDView


def get_app():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    return app


def test_set_detail_data_populates_qabstracttablemodel():
    get_app()
    view = SLDView()

    rel = RelationshipRow("A", "Parent", "Type1")
    view.set_detail_data(rel)

    assert view.detail_model.rowCount() == 3
    assert view.detail_model.data(view.detail_model.index(2, 1), Qt.DisplayRole) == "Type1"
