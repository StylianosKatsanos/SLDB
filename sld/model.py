
# -*- coding: utf-8 -*-
from __future__ import annotations

import pathlib
import sqlite3
import pandas as pd
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class RelationshipRow:
    entry_name: str
    attached_to: str
    entry_type: Optional[str] = None


class SLDModel:
    """SQLite data-access layer."""

    def __init__(self, db_path: pathlib.Path, project_name) -> None:
        self.db_path = pathlib.Path(db_path)
        self.project_name = project_name

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

    def ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS Relationships (
                    Entry_name TEXT PRIMARY KEY,
                    Attached_to TEXT,
                    Type TEXT
                )
                """
            )
            conn.commit()
            
            
        self.ensure_root_node(self.project_name)
    
    
    def ensure_root_node(self, project_name: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            
            cur.execute("""
                SELECT COUNT(*)
                FROM Relationships
                WHERE Type = 'PROJECT'
            """)
            
            exists = cur.fetchone()[0]
            
            if not exists:
                cur.execute("""
                    INSERT INTO Relationships
                    (
                        Entry_name,
                        Attached_to,
                        Type
                    )
                    VALUES (?,?,?)
                """, (
                project_name,
                None,
                "PROJECT"
            ))
                
            conn.commit()
    
    
    def fetch_relationships(self) -> List[RelationshipRow]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT Entry_name, Attached_to, Type 
                FROM Relationships 
                ORDER BY Entry_name"""
            ).fetchall()
        return [
            RelationshipRow(row["Entry_name"], row["Attached_to"] or "", row["Type"])
            for row in rows
        ]

    def get_relationship(self, entry_name: str) -> Optional[RelationshipRow]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT Entry_name, Attached_to, Type FROM Relationships WHERE Entry_name = ?",
                (entry_name,),
            ).fetchone()
        if not row:
            return None
        return RelationshipRow(row["Entry_name"], row["Attached_to"] or "", row["Type"])

    def exists(self, entry_name: str) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM Relationships WHERE Entry_name = ?",
                (entry_name,),
            ).fetchone()
        return row is not None

    def add_relationship(self, rel: RelationshipRow) -> None:
        
        attached_to = rel.attached_to
        if rel.attached_to == '':
            attached_to = self.project_name
            print(attached_to)
        
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO Relationships (Entry_name, Attached_to, Type) VALUES (?, ?, ?)",
                (rel.entry_name, attached_to, rel.entry_type),
            )
            conn.commit()
            
    def add_multiple_relationships(self, rows: List[RelationshipRow]) -> None:
        if not rows:
            return
        
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT INTO Relationships (Entry_name, Attached_to, Type)
                VALUES (?, ?, ?)
                """,
                [(r.entry_name, r.attached_to, r.entry_type) for r in rows],
            )
            conn.commit()

    def update_relationship_field(self, entry_name: str, field: str, value: Optional[str]) -> None:
        allowed = {"Attached_to", "Type"}
        if field not in allowed:
            raise ValueError(f"Unsupported field update: {field}")
        with self._connect() as conn:
            conn.execute(
                f"UPDATE Relationships SET {field} = ? WHERE Entry_name = ?",
                (value, entry_name),
            )
            conn.commit()

    def rename_relationship(self, old_name: str, new_name: str) -> None:
        if old_name == new_name:
            return
        with self._connect() as conn:
            if conn.execute(
                "SELECT 1 FROM Relationships WHERE Entry_name = ?",
                (new_name,),
            ).fetchone():
                raise ValueError(f"An entry named '{new_name}' already exists.")
            conn.execute(
                "UPDATE Relationships SET Entry_name = ? WHERE Entry_name = ?",
                (new_name, old_name),
            )
            conn.execute(
                "UPDATE Relationships SET Attached_to = ? WHERE Attached_to = ?",
                (new_name, old_name),
            )
            conn.commit()

    def update_relationship(self, old_name: str, rel: RelationshipRow) -> None:
        with self._connect() as conn:
            if old_name != rel.entry_name:
                existing = conn.execute(
                    "SELECT 1 FROM Relationships WHERE Entry_name = ?",
                    (rel.entry_name,),
                ).fetchone()
                if existing:
                    raise ValueError(f"An entry named '{rel.entry_name}' already exists.")
            conn.execute(
                "UPDATE Relationships SET Entry_name = ?, Attached_to = ?, Type = ? WHERE Entry_name = ?",
                (rel.entry_name, rel.attached_to, rel.entry_type, old_name),
            )
            if old_name != rel.entry_name:
                conn.execute(
                    "UPDATE Relationships SET Attached_to = ? WHERE Attached_to = ?",
                    (rel.entry_name, old_name),
                )
            conn.commit()

    def delete_relationship(self, entry_name: str, reattach_children_to_parent: bool = True) -> None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT Attached_to FROM Relationships WHERE Entry_name = ?",
                (entry_name,),
            ).fetchone()
            if not row:
                return
            parent_name = row["Attached_to"] or ""
            if reattach_children_to_parent:
                conn.execute(
                    "UPDATE Relationships SET Attached_to = ? WHERE Attached_to = ?",
                    (parent_name, entry_name),
                )
            else:
                conn.execute(
                    "UPDATE Relationships SET Attached_to = '' WHERE Attached_to = ?",
                    (entry_name,),
                )
            conn.execute("DELETE FROM Relationships WHERE Entry_name = ?", (entry_name,))
            conn.commit()
    
    
    def export_database(self, csv_path, table_name = "Relationships") -> None:
        
        query = f"""
        SELECT 
            Entry_name,
            Attached_to, 
            Type 
        FROM {table_name}
        ORDER BY Entry_name
        """
        
        with self._connect() as conn:
            df = pd.read_sql_query(query, conn)
            
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    
    def close(self) -> None:
        # Connections are short-lived, so there is nothing persistent to close.
        pass
        
