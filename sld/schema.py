
# -*- coding: utf-8 -*-
"""SLD database schema and the one-off migration from the old name-keyed format.

Old format:  Relationships(Entry_name TEXT PRIMARY KEY, Attached_to TEXT[, Type TEXT])
             where Attached_to holds the parent's name.
New format:  Relationships(NodeID, Entry_name UNIQUE, ParentID -> NodeID, Type)
"""
from __future__ import annotations

import pathlib
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from typing import List

CREATE_RELATIONSHIPS = """
    CREATE TABLE IF NOT EXISTS Relationships (
        NodeID     INTEGER PRIMARY KEY AUTOINCREMENT,
        Entry_name TEXT NOT NULL UNIQUE,
        ParentID   INTEGER REFERENCES Relationships(NodeID),
        Type       TEXT
    )
"""


class LegacySchemaError(RuntimeError):
    """Raised when an old-format SLD database cannot be migrated."""


@dataclass
class MigrationResult:
    """What a migration did, so the UI can tell the user."""
    backup_path: pathlib.Path
    node_count: int
    # Nodes whose old parent name did not match any node; they now have no parent.
    unmatched_parents: List[str] = field(default_factory=list)


def relationship_columns(conn: sqlite3.Connection) -> List[str]:
    return [row[1] for row in conn.execute("PRAGMA table_info(Relationships)")]


def is_legacy(conn: sqlite3.Connection) -> bool:
    """True when the Relationships table exists but has no NodeID column."""
    columns = relationship_columns(conn)
    return bool(columns) and "NodeID" not in columns


def _backup_path_for(db_path: pathlib.Path) -> pathlib.Path:
    # ".bak" keeps the backup out of the "*.db" filter in the Open SLD dialog.
    path = db_path.with_name(f"{db_path.name}.pre-nodeid.bak")
    if path.exists():
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        path = db_path.with_name(f"{db_path.name}.pre-nodeid-{stamp}.bak")
    return path


def _backup(db_path: pathlib.Path) -> pathlib.Path:
    """Copy the database with SQLite's backup API (includes unsaved WAL pages)."""
    backup_path = _backup_path_for(db_path)
    src = sqlite3.connect(str(db_path))
    dst = sqlite3.connect(str(backup_path))
    try:
        src.backup(dst)
    finally:
        dst.close()
        src.close()
    return backup_path


def migrate_legacy(db_path: pathlib.Path) -> MigrationResult:
    """Convert an old name-keyed SLD database to NodeIDs, in place.

    A backup is written first. The conversion runs in one transaction, so on
    any error the database is left exactly as it was.
    """
    db_path = pathlib.Path(db_path)
    conn = sqlite3.connect(str(db_path), timeout=10, isolation_level=None)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        columns = relationship_columns(conn)
        if not columns or "NodeID" in columns:
            raise LegacySchemaError(f"'{db_path.name}' is not an old-format SLD database.")
        if "Entry_name" not in columns or "Attached_to" not in columns:
            raise LegacySchemaError(
                f"'{db_path.name}' has an unexpected Relationships table: {', '.join(columns)}."
            )
        blank = conn.execute(
            "SELECT COUNT(*) FROM Relationships WHERE Entry_name IS NULL OR TRIM(Entry_name) = ''"
        ).fetchone()[0]
        if blank:
            raise LegacySchemaError(
                f"'{db_path.name}' has {blank} node(s) without a name; fix them before migrating."
            )

        backup_path = _backup(db_path)
        type_column = "Type" if "Type" in columns else "NULL"

        conn.execute("BEGIN IMMEDIATE")
        try:
            conn.execute("ALTER TABLE Relationships RENAME TO Relationships_legacy")
            conn.execute(CREATE_RELATIONSHIPS)
            # Keep the original order so NodeIDs follow the order nodes were created.
            conn.execute(
                f"""
                INSERT INTO Relationships (Entry_name, Type)
                SELECT Entry_name, {type_column} FROM Relationships_legacy ORDER BY rowid
                """
            )
            # Parent name -> parent NodeID. Blank, self-referencing and unknown
            # parents become NULL, which is how the old tree already showed them.
            conn.execute(
                """
                UPDATE Relationships
                SET ParentID = (
                    SELECT p.NodeID
                    FROM Relationships_legacy AS l
                    JOIN Relationships AS p ON p.Entry_name = l.Attached_to
                    WHERE l.Entry_name = Relationships.Entry_name
                      AND l.Attached_to <> l.Entry_name
                )
                """
            )
            unmatched = [
                row[0]
                for row in conn.execute(
                    """
                    SELECT l.Entry_name
                    FROM Relationships_legacy AS l
                    WHERE TRIM(COALESCE(l.Attached_to, '')) <> ''
                      AND l.Attached_to <> l.Entry_name
                      AND l.Attached_to NOT IN (SELECT Entry_name FROM Relationships_legacy)
                    ORDER BY l.Entry_name
                    """
                )
            ]
            node_count = conn.execute("SELECT COUNT(*) FROM Relationships").fetchone()[0]
            conn.execute("DROP TABLE Relationships_legacy")
            problems = conn.execute("PRAGMA foreign_key_check(Relationships)").fetchall()
            if problems:
                raise LegacySchemaError(f"Migration produced {len(problems)} invalid parent link(s).")
            conn.execute("COMMIT")
        except BaseException:
            conn.execute("ROLLBACK")
            raise
    finally:
        conn.close()
    return MigrationResult(backup_path, node_count, unmatched)
