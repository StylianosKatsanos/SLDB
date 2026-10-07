from config.paths import DATABASE_ROOT, SLD_DB_ROOT

def test_sld_folder_matches_repository_folder() -> None:
    # Linux and macOS are case-sensitive: the configured name must match exactly.
    folder_names = [p.name for p in DATABASE_ROOT.iterdir() if p.is_dir()]

    assert SLD_DB_ROOT.name in folder_names
    assert SLD_DB_ROOT.name == "sld_databases"
