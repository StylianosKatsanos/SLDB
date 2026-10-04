
# -*- coding: utf-8 -*-
from __future__ import annotations

import pathlib
import sqlite3
import pandas as pd
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator, List, Optional

# LegacySchemaError is re-exported for callers that import it from sld.model.
from .schema import CREATE_RELATIONSHIPS, LegacySchemaError, MigrationResult, is_legacy, migrate_legacy  # noqa: F401


# Type of the single project root node.
ROOT_TYPE = "PROJECT"


@dataclass
class RelationshipRow:
    """One SLD node.

    ``node_id`` and ``parent_id`` identify the node and its parent in the
    database. They are internal and must never be shown in the view; the view
    works with ``entry_name`` and ``attached_to`` (the parent's name).
    """
    entry_name: str
    attached_to: str
    entry_type: Optional[str] = None
    node_id: Optional[int] = None
    parent_id: Optional[int] = None


class SLDModel:
    """SQLite data-access layer.

    Nodes are identified by ``NodeID``. Parent links are stored as
    ``ParentID`` (a foreign key to ``NodeID``); ``Entry_name`` stays unique.

    The project root is the single node with Type ``PROJECT``. It always
    exists, has no parent, keeps its type and cannot be renamed or deleted
    by the user; its name comes from the DB Client project.
    """

    ROOT_TYPE = ROOT_TYPE

    def __init__(self, db_path: pathlib.Path, project_name, sync_root_name: bool = False) -> None:
        """``sync_root_name``: rename the root to ``project_name`` on open. Only set
        it when ``project_name`` is the DB Client's project name (not a file name)."""
        self.db_path = pathlib.Path(db_path)
        self.project_name = project_name
        self.sync_root_name = sync_root_name
        # Set when ensure_schema() converted an old-format file.
        self.last_migration: Optional[MigrationResult] = None

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(
            str(self.db_path),
            timeout=10,
            isolation_level=None,
        )
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.row_factory = sqlite3.Row
        return conn

    @contextmanager
    def _transaction(self) -> Iterator[sqlite3.Connection]:
        """Open a connection, run the block in one transaction, then close it."""
        conn = self._connect()
        try:
            conn.execute("BEGIN")
            try:
                yield conn
            except BaseException:
                conn.execute("ROLLBACK")
                raise
            conn.execute("COMMIT")
        finally:
            conn.close()

    # ---------------- Schema ----------------

    def ensure_schema(self) -> None:
        """Create the table, converting an old name-keyed file first if needed."""
        conn = self._connect()
        try:
            legacy = is_legacy(conn)
        finally:
            conn.close()
        if legacy:
            self.last_migration = migrate_legacy(self.db_path)
        with self._transaction() as conn:
            conn.execute(CREATE_RELATIONSHIPS)
        self.ensure_root_node(self.project_name)

    def ensure_root_node(self, project_name: str) -> None:
        """Make sure the project root exists (repairing it if its type was changed)."""
        with self._transaction() as conn:
            root_id = self._root_id(conn)
            if root_id is None:
                same_name = conn.execute(
                    "SELECT NodeID, ParentID FROM Relationships WHERE Entry_name = ?",
                    (project_name,),
                ).fetchone()
                if same_name is None:
                    conn.execute(
                        "INSERT INTO Relationships (Entry_name, ParentID, Type) VALUES (?, NULL, ?)",
                        (project_name, self.ROOT_TYPE),
                    )
                    return
                if same_name["ParentID"] is not None:
                    raise ValueError(
                        f"'{project_name}' is attached to another node, so it cannot be restored "
                        "as the project root."
                    )
                # The root lost its PROJECT type (possible before the root was protected).
                conn.execute(
                    "UPDATE Relationships SET Type = ? WHERE NodeID = ?",
                    (self.ROOT_TYPE, same_name["NodeID"]),
                )
                return
            if self.sync_root_name and project_name:
                self._check_name_free(conn, project_name, root_id)
                conn.execute(
                    "UPDATE Relationships SET Entry_name = ? WHERE NodeID = ?",
                    (project_name, root_id),
                )

    def _root_id(self, conn: sqlite3.Connection) -> Optional[int]:
        row = conn.execute(
            "SELECT NodeID FROM Relationships WHERE Type = ? ORDER BY NodeID LIMIT 1",
            (self.ROOT_TYPE,),
        ).fetchone()
        return row["NodeID"] if row else None

    def _check_root_rules(
        self,
        conn: sqlite3.Connection,
        node_id: Optional[int],
        *,
        name: Optional[str] = None,
        parent_id: Optional[int] = None,
        entry_type: Optional[str] = None,
        changes: tuple = (),
    ) -> None:
        """Reject changes that would break the project root.

        ``changes`` lists which of "name", "parent", "type" are being set.
        """
        root_id = self._root_id(conn)
        if node_id is not None and node_id == root_id:
            current = conn.execute(
                "SELECT Entry_name FROM Relationships WHERE NodeID = ?", (node_id,)
            ).fetchone()
            if "name" in changes and current and name != current["Entry_name"]:
                raise ValueError("The project node's name comes from the DB Client and cannot be changed.")
            if "parent" in changes and parent_id is not None:
                raise ValueError("The project node cannot be attached to another node.")
            if "type" in changes and entry_type != self.ROOT_TYPE:
                raise ValueError("The project node's type cannot be changed.")
        elif "type" in changes and entry_type == self.ROOT_TYPE:
            raise ValueError(f"Only the project node can have the type '{self.ROOT_TYPE}'.")

    def root_node_id(self) -> Optional[int]:
        with self._transaction() as conn:
            return self._root_id(conn)

    def is_root(self, node_id: Optional[int]) -> bool:
        return node_id is not None and node_id == self.root_node_id()

    # ---------------- Queries ----------------

    _SELECT_NODES = """
        SELECT n.NodeID, n.Entry_name, n.ParentID, n.Type, p.Entry_name AS Parent_name
        FROM Relationships AS n
        LEFT JOIN Relationships AS p ON p.NodeID = n.ParentID
    """

    @staticmethod
    def _to_row(row: sqlite3.Row) -> RelationshipRow:
        return RelationshipRow(
            entry_name=row["Entry_name"],
            attached_to=row["Parent_name"] or "",
            entry_type=row["Type"],
            node_id=row["NodeID"],
            parent_id=row["ParentID"],
        )

    def fetch_relationships(self) -> List[RelationshipRow]:
        with self._transaction() as conn:
            rows = conn.execute(self._SELECT_NODES + " ORDER BY n.Entry_name").fetchall()
        return [self._to_row(row) for row in rows]

    def get_relationship(self, node_id: int) -> Optional[RelationshipRow]:
        with self._transaction() as conn:
            row = conn.execute(self._SELECT_NODES + " WHERE n.NodeID = ?", (node_id,)).fetchone()
        return self._to_row(row) if row else None

    def get_node_id(self, entry_name: str) -> Optional[int]:
        """Resolve a user-visible name to its NodeID."""
        with self._transaction() as conn:
            row = conn.execute(
                "SELECT NodeID FROM Relationships WHERE Entry_name = ?",
                (entry_name,),
            ).fetchone()
        return row["NodeID"] if row else None

    def exists(self, entry_name: str) -> bool:
        return self.get_node_id(entry_name) is not None

    # ---------------- Changes ----------------

    @staticmethod
    def _check_name_free(conn: sqlite3.Connection, entry_name: str, node_id: Optional[int] = None) -> None:
        row = conn.execute(
            "SELECT NodeID FROM Relationships WHERE Entry_name = ?",
            (entry_name,),
        ).fetchone()
        if row and row["NodeID"] != node_id:
            raise ValueError(f"An entry named '{entry_name}' already exists.")

    def _parent_or_root(self, conn: sqlite3.Connection, parent_id: Optional[int]) -> Optional[int]:
        """Nodes added without a parent are attached to the project root."""
        if parent_id is not None:
            return parent_id
        return self._root_id(conn)

    def add_relationship(self, rel: RelationshipRow) -> int:
        """Insert one node and return its new NodeID."""
        with self._transaction() as conn:
            self._check_name_free(conn, rel.entry_name)
            self._check_root_rules(conn, None, entry_type=rel.entry_type, changes=("type",))
            cur = conn.execute(
                "INSERT INTO Relationships (Entry_name, ParentID, Type) VALUES (?, ?, ?)",
                (rel.entry_name, self._parent_or_root(conn, rel.parent_id), rel.entry_type),
            )
            return cur.lastrowid

    def add_multiple_relationships(self, rows: List[RelationshipRow]) -> List[int]:
        """Insert several nodes in one transaction and return their NodeIDs."""
        new_ids: List[int] = []
        if not rows:
            return new_ids
        with self._transaction() as conn:
            for rel in rows:
                self._check_name_free(conn, rel.entry_name)
                self._check_root_rules(conn, None, entry_type=rel.entry_type, changes=("type",))
                cur = conn.execute(
                    "INSERT INTO Relationships (Entry_name, ParentID, Type) VALUES (?, ?, ?)",
                    (rel.entry_name, self._parent_or_root(conn, rel.parent_id), rel.entry_type),
                )
                new_ids.append(cur.lastrowid)
        return new_ids

    def update_relationship_field(self, node_id: int, field: str, value) -> None:
        allowed = {"ParentID", "Type"}
        if field not in allowed:
            raise ValueError(f"Unsupported field update: {field}")
        with self._transaction() as conn:
            if field == "ParentID":
                self._check_root_rules(conn, node_id, parent_id=value, changes=("parent",))
            else:
                self._check_root_rules(conn, node_id, entry_type=value, changes=("type",))
            conn.execute(
                f"UPDATE Relationships SET {field} = ? WHERE NodeID = ?",
                (value, node_id),
            )

    def rename_relationship(self, node_id: int, new_name: str) -> None:
        # Children reference the NodeID, so only this row changes.
        with self._transaction() as conn:
            self._check_name_free(conn, new_name, node_id)
            self._check_root_rules(conn, node_id, name=new_name, changes=("name",))
            conn.execute(
                "UPDATE Relationships SET Entry_name = ? WHERE NodeID = ?",
                (new_name, node_id),
            )

    def update_relationship(self, rel: RelationshipRow) -> None:
        """Update name, parent and type of the node identified by ``rel.node_id``."""
        if rel.node_id is None:
            raise ValueError("Cannot update a node without a NodeID.")
        with self._transaction() as conn:
            self._check_name_free(conn, rel.entry_name, rel.node_id)
            self._check_root_rules(
                conn,
                rel.node_id,
                name=rel.entry_name,
                parent_id=rel.parent_id,
                entry_type=rel.entry_type,
                changes=("name", "parent", "type"),
            )
            conn.execute(
                "UPDATE Relationships SET Entry_name = ?, ParentID = ?, Type = ? WHERE NodeID = ?",
                (rel.entry_name, rel.parent_id, rel.entry_type, rel.node_id),
            )

    def delete_relationship(self, node_id: int, reattach_children_to_parent: bool = True) -> None:
        with self._transaction() as conn:
            if node_id == self._root_id(conn):
                raise ValueError("The project node cannot be deleted.")
            row = conn.execute(
                "SELECT ParentID FROM Relationships WHERE NodeID = ?",
                (node_id,),
            ).fetchone()
            if not row:
                return
            new_parent = row["ParentID"] if reattach_children_to_parent else None
            conn.execute(
                "UPDATE Relationships SET ParentID = ? WHERE ParentID = ?",
                (new_parent, node_id),
            )
            conn.execute("DELETE FROM Relationships WHERE NodeID = ?", (node_id,))

    # ---------------- Export ----------------

    def export_database(self, csv_path) -> None:
        query = """
        SELECT
            n.NodeID,
            n.Entry_name,
            p.Entry_name AS Attached_to,
            n.Type
        FROM Relationships AS n
        LEFT JOIN Relationships AS p ON p.NodeID = n.ParentID
        ORDER BY n.Entry_name
        """
        conn = self._connect()
        try:
            df = pd.read_sql_query(query, conn)
        finally:
            conn.close()
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    def close(self) -> None:
        # Every method opens and closes its own connection, so nothing stays open.
        pass
