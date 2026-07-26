
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from detail_table_model import DetailTableModel
from model import RelationshipRow


def get_app():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    return app


def test_set_relationship_populates_three_rows():
    get_app()
    model = DetailTableModel()
    model.set_relationship(RelationshipRow("Node A", "Root", "Transformer"))

    assert model.rowCount() == 3
    assert model.columnCount() == 2
    assert model.data(model.index(0, 0), Qt.DisplayRole) == "Entry Name"
    assert model.data(model.index(0, 1), Qt.DisplayRole) == "Node A"


def test_second_column_is_editable_and_emits_value_changed():
    get_app()
    model = DetailTableModel()
    model.set_relationship(RelationshipRow("Node A", "Root", "Transformer"))

    captured = []
    model.value_changed.connect(lambda field, value: captured.append((field, value)))

    changed = model.setData(model.index(1, 1), "Parent X", Qt.EditRole)

    assert changed is True
    assert model.data(model.index(1, 1), Qt.DisplayRole) == "Parent X"
    assert captured == [("Attached To", "Parent X")]
