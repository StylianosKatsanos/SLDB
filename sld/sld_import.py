# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import pathlib
import collections

from dataclasses import dataclass, field
from typing import List, Optional

from config.paths import SLD_DB_ROOT
from sld.types_config import TYPES

REQUIRED = ['Entry_name', 'Attached_to', 'Type']

@dataclass
class ImportRow:

    line: int
    name: str
    parent_name: Optional[str]
    entry_type: Optional[str] = None

@dataclass
class ImportReport:

    rows: List[ImportRow]
    root_name: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

def _clean(value):
    value = (value or '').strip()
    return value or None

def _read_sld_csv(path: pathlib.Path) -> List[ImportRow]:

    if not path.exists():
        raise ValueError('File does not exist')

    with path.open("r", newline="", encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)

        if not reader.fieldnames:
            raise ValueError('CSV does not contain required fields')

        missing = [col for col in REQUIRED if col not in reader.fieldnames]
        if missing:
            raise ValueError(f"Missing column(s): {', '.join(missing)}")

        rows = []

        for line, row in enumerate(reader, start=2):
            entry = ImportRow(line = line,
                              name = (row.get("Entry_name") or "").strip(),
                              parent_name = _clean(row.get("Attached_to")),
                              entry_type = _clean(row.get("Type"))
                              )

            rows.append(entry)

        return rows

def _validate_rows(rows: List[ImportRow]) -> ImportReport:

    report = ImportReport(rows=rows)

    # Step 1: Pre-row Checks

    allowed = {t for items in TYPES.values() for t in items} | {"PROJECT"}

    for row in rows:
        if not row.name:
            report.errors.append(f'Empty Name in line {row.line}')
        if row.entry_type not in TYPES and row.entry_type not in allowed:
            report.warnings.append(f'Unknown entry type {row.entry_type} in line {row.line}')
        if row.name == row.parent_name:
            report.errors.append(f'Attached to itself in line {row.line}')


    # Step 2: Build lookup structures
    names_counter = collections.defaultdict(list)
    parent_of = {row.name : row.parent_name for row in rows if row.name}

    for row in rows:
        if row.name:
            names_counter[row.name].append(row.line)

    # Step 3 Check for duplicate names

    for name, lines in names_counter.items():
        if len(lines) > 1:
            report.errors.append(f'Name {name} appears more than once in the following lines: {lines}')

    # Step 4 Check Root of project

    project_rows = [row for row in rows if row.entry_type == "PROJECT"]
    if len(project_rows) != 1:
        report.errors.append(f'Multiple project roots in file')
    project_with_parent = [row.line for row in rows if row.parent_name and row.entry_type == "PROJECT"]
    if len(project_with_parent) != 0:
        report.errors.append(f'Multiple project roots with parent in file')
    if project_rows:
        report.root_name = project_rows[0].name


    # Step 5 Parents exist

    rows_with_parents = [row for row in rows if row.parent_name]
    for row in rows_with_parents:
        if row.parent_name not in names_counter.keys():
            report.errors.append(f'Line {row.line}: Parent name {row.parent_name} not found')

    # Step 6 Cycle detection

    _check_cycles(rows, parent_of, names_counter, report.root_name, report)

    return report


def _check_cycles(rows, parent_of, lines_by_name, root_name, report) -> None:
    """Report every loop in the parent links (A → B → C → A) once."""
    reported = set()                          # cycles already reported, as frozensets of names

    for row in rows:
        if not row.name or row.parent_name == row.name:
            continue                          # empty names and self-links are reported in step 1

        path = [row.name]                     # the chain walked so far, in order
        current = row.parent_name

        while current is not None and current != root_name:
            if current in path:               # back to a node on this chain: a cycle
                cycle = path[path.index(current):]
                key = frozenset(cycle)
                if key not in reported:
                    reported.add(key)
                    chain = " → ".join(cycle + [current])
                    lines = ", ".join(str(lines_by_name[n][0]) for n in cycle)
                    report.errors.append(f"Cycle in parent links: {chain} (lines {lines})")
                break
            if current not in parent_of:      # unknown parent, already reported in step 5
                break
            path.append(current)
            current = parent_of[current]

def _load_sld_csv(path: pathlib.Path) -> ImportReport:
    try:
        rows = _read_sld_csv(path)
    except FileNotFoundError:
        return ImportReport(rows=[], errors=[f"File not found: {path}"])
    except UnicodeDecodeError:
        return ImportReport(rows=[], errors=["The file is not UTF-8. Save it as 'CSV UTF-8' and try again."])
    except ValueError as exc:
        return ImportReport(rows=[], errors=[str(exc)])

    return _validate_rows(rows)

if "__main__" == __name__:

    root = SLD_DB_ROOT/"raw_database.csv"

    reader = _load_sld_csv(root)
    print(reader)

