from .sld_import import load_sld_csv

def write_csv(tmp_path, text):
    path = tmp_path / "import.csv"
    path.write_text(text, encoding="utf-8-sig")   # same BOM as a real export
    return path

def test_duplicate_name_is_an_error(tmp_path):
    path = write_csv(tmp_path, "Entry_name,Attached_to,Type\n"
                               "Project X,,PROJECT\n"
                               "Plot 1,Project X,Plot\n"
                               "Plot 1,Project X,Plot\n")
    report = load_sld_csv(path)
    assert not report.ok
    assert any("Plot 1" in e and "3" in e for e in report.errors)


def test_empty_csv():
    load_sld_csv()