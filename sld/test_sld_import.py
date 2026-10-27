from sld.sld_import import load_sld_csv

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

def test_no_project_error(tmp_path):
    path = write_csv(tmp_path, "Entry_name,Attached_to,Type\n"
                     "Plot X,,Plot\n"
                     "HV 1,Plot X,HV\n"
                     "HV 2,Plot X,HV\n"
                     "Main 11,HV 1,Main\n"
                     "Main 12,HV 1,Main\n"
                     "Main 21,HV 2,Main\n"
                     "Main 22,HV 2,Main\n")
    report = load_sld_csv(path)
    assert not report.ok
    assert any("No project" in e for e in report.errors)


def test_empty_csv(tmp_path):
    report = load_sld_csv(write_csv(tmp_path, ""))
    assert not report.ok
    assert any("required fields" in e for e in report.errors)