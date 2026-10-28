from sld.sld_import import load_sld_csv, ImportRow, _validate_rows

HEADER = "Entry_name,Attached_to,Type\n"


def write_csv(tmp_path, text):
    path = tmp_path / "import.csv"
    path.write_text(text, encoding="utf-8-sig")   # same BOM as a real export
    return path

def row(line, name, parent=None, entry_type="Plot"):
    return ImportRow(line=line, name=name, parent_name=parent, entry_type=entry_type)

ROOT = row(2, "Project X", None, "PROJECT")

def errors_with(report, *words):
    """Errors that contain all the given words."""
    return [e for e in report.errors if all(w in e for w in words)]

# ----------------------- Reading the file ---------------------

# ---------------- Reading the file ----------------

def test_valid_export_with_node_id(tmp_path):
    path = write_csv(tmp_path, "NodeID,Entry_name,Attached_to,Type\n"
                               "1,Project X,,PROJECT\n"
                               "2,Plot 1,Project X,Plot\n"
                               "3,CB_1,Plot 1,Ciruit Breaker\n")
    report = load_sld_csv(path)
    assert report.ok
    assert report.warnings == []
    assert report.root_name == "Project X"
    assert [r.name for r in report.rows] == ["Project X", "Plot 1", "CB_1"]

def test_values_are_stripped_and_empty_becomes_none(tmp_path):
    path = write_csv(tmp_path, HEADER +
                     "Project X,,PROJECT\n"
                     "  Plot 1 , Project X ,  \n")
    plot = load_sld_csv(path).rows[1]
    assert (plot.name, plot.parent_name, plot.entry_type) == ("Plot 1", "Project X", None)

def test_line_numbers_start_after_header(tmp_path):
    path = write_csv(tmp_path, HEADER + "Project X,,PROJECT\nPlot 1,Project X,Plot\n")
    assert [r.line for r in load_sld_csv(path).rows] == [2, 3]

def test_missing_column(tmp_path):
    report = load_sld_csv(write_csv(tmp_path, "Entry_name,Type\nPlot 1,Plot\n"))
    assert not report.ok
    assert errors_with(report, "Attached_to")

def test_empty_csv(tmp_path):
    report = load_sld_csv(write_csv(tmp_path, ""))
    assert not report.ok
    assert report.rows == []

def test_missing_file(tmp_path):
    report = load_sld_csv(tmp_path / "does_not_exist.csv")
    assert not report.ok
    assert errors_with(report, "not found")

def test_file_not_utf8(tmp_path):
    path = tmp_path / "excel.csv"
    path.write_bytes((HEADER + "Project X,,PROJECT\nPlot é,Project X,Plot\n").encode("cp1252"))
    report = load_sld_csv(path)
    assert not report.ok
    assert errors_with(report, "UTF-8")

# ---------------- Row checks ----------------

def test_empty_name_is_an_error():
    report = _validate_rows([ROOT, row(3, "", "Project X")])
    assert errors_with(report, "3")
    assert not report.ok

def test_unknown_type_is_only_a_warning():
    report = _validate_rows([ROOT, row(3, "Trafo 1", "Project X", "Trafo")])
    assert report.ok
    assert any("Trafo" in w and "3" in w for w in report.warnings)

def test_empty_type_gives_no_warning():
    report = _validate_rows([ROOT, row(3, "Spare", "Project X", None)])
    assert report.ok
    assert report.warnings == []

def test_attached_to_itself_is_an_error():
    report = _validate_rows([ROOT, row(3, "Plot 1", "Plot 1")])
    assert not report.ok
    assert errors_with(report, "3")

# ---------------- Duplicates ----------------

def test_duplicate_name_is_an_error(tmp_path):
    path = write_csv(tmp_path, HEADER +
                     "Project X,,PROJECT\n"
                     "Plot 1,Project X,Plot\n"
                     "Plot 1,Project X,Plot\n")
    report = load_sld_csv(path)
    assert not report.ok
    assert errors_with(report, "Plot 1", "3", "4")

# ---------------- Root ----------------

def test_no_project_is_an_error(tmp_path):
    path = write_csv(tmp_path, HEADER +
                     "Plot X,,Plot\n"
                     "HV 1,Plot X,HV\n"
                     "Main 11,HV 1,Main\n")
    report = load_sld_csv(path)
    assert not report.ok
    assert len(report.errors) == 1
    assert errors_with(report, "No project")
    assert report.root_name is None

def test_two_projects_is_an_error():
    report = _validate_rows([ROOT, row(3, "Project Y", None, "PROJECT"), row(4, "Plot 1", "Project X")])
    assert not report.ok
    assert errors_with(report, "Multiple")

def test_project_with_parent_is_an_error():
    report = _validate_rows([row(2, "Plot 1", None), row(3, "Project X", "Plot 1", "PROJECT")])
    assert not report.ok
    assert errors_with(report, "Line 3")

# ---------------- Parents ----------------

def test_missing_parent_is_an_error():
    report = _validate_rows([ROOT, row(3, "Plot 1", "Ghost")])
    assert not report.ok
    assert errors_with(report, "Ghost", "3")

def test_child_before_parent_is_fine():
    report = _validate_rows([row(2, "CB_1", "Plot 1", "Ciruit Breaker"),
                             row(3, "Plot 1", "Project X"),
                             row(4, "Project X", None, "PROJECT")])
    assert report.ok
    assert report.root_name == "Project X"

# ---------------- Cycles ----------------

def test_cycle_is_reported_once():
    # A -> C -> B -> A, and X leads into the loop: one error, not four.
    report = _validate_rows([ROOT,
                             row(3, "A", "C"),
                             row(4, "B", "A"),
                             row(5, "C", "B"),
                             row(6, "X", "A")])
    cycle_errors = errors_with(report, "Cycle")
    assert len(cycle_errors) == 1
    assert all(name in cycle_errors[0] for name in ("A", "B", "C"))
    assert "X" not in cycle_errors[0]

def test_two_separate_cycles_are_both_reported():
    report = _validate_rows([ROOT,
                             row(3, "A", "B"), row(4, "B", "A"),
                             row(5, "C", "D"), row(6, "D", "C")])
    assert len(errors_with(report, "Cycle")) == 2

def test_deep_tree_has_no_cycle():
    rows = [ROOT] + [row(i + 3, f"N{i}", "Project X" if i == 0 else f"N{i - 1}") for i in range(50)]
    assert _validate_rows(rows).ok

# ---------------- Nothing to import ----------------

def test_only_root_gives_a_warning():
    report = _validate_rows([ROOT])
    assert report.ok
    assert report.warnings

def test_header_only_gives_a_warning(tmp_path):
    report = load_sld_csv(write_csv(tmp_path, HEADER))
    assert report.warnings