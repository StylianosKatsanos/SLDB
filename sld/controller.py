
# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Dict, List, Optional, Set

from PySide6.QtWidgets import QTreeWidgetItem

from .model import RelationshipRow, SLDModel
from .view import SLDView


class SLDController:
    """Connects the SLD view to the model.

    Works with NodeIDs internally; the user only ever sees and types names.
    After every change the tree is reloaded from the database, so the view
    never shows stale names or parents.
    """

    def __init__(self, model: SLDModel, view: SLDView) -> None:
        self.model = model
        self.view = view
        self.view.selection_changed.connect(self.on_tree_selection_changed)
        self.view.detail_value_changed.connect(self.on_detail_value_changed)
        self.view.add_requested.connect(self.add_node)
        self.view.edit_requested.connect(self.edit_node)
        self.view.delete_requested.connect(self.delete_node)
        self.model.ensure_schema()
        self.reload_tree()

    # ---------------- Tree ----------------

    def reload_tree(self, select_node_id: Optional[int] = None) -> None:
        relationships = self.model.fetch_relationships()
        self.view.clear_tree()
        by_id = {rel.node_id: rel for rel in relationships}
        children: Dict[int, List[RelationshipRow]] = {}
        root_rows: List[RelationshipRow] = []
        for rel in relationships:
            parent_id = rel.parent_id
            if parent_id is None or parent_id == rel.node_id or parent_id not in by_id:
                root_rows.append(rel)
            else:
                children.setdefault(parent_id, []).append(rel)

        def add_subtree(parent_item: Optional[QTreeWidgetItem], rel: RelationshipRow, visited: Set[int]) -> None:
            if rel.node_id in visited:
                return
            visited = visited | {rel.node_id}
            item = self.view.add_tree_item(parent_item, rel)
            for child in sorted(children.get(rel.node_id, []), key=lambda x: x.entry_name.lower()):
                add_subtree(item, child, visited)

        for root in sorted(root_rows, key=lambda x: x.entry_name.lower()):
            add_subtree(None, root, set())
        self.view.expand_all()

        if select_node_id is not None and self.view.select_node(select_node_id):
            return
        top = self.view.tree.topLevelItem(0)
        if top is not None:
            self.view.tree.setCurrentItem(top)
        else:
            self.view.set_detail_data(None)

    # ---------------- Parent checks ----------------

    def _resolve_parent(self, parent_name: str) -> Optional[int]:
        """Turn the parent name the user typed into a NodeID (blank means no parent)."""
        parent_name = (parent_name or "").strip()
        if not parent_name:
            return None
        parent_id = self.model.get_node_id(parent_name)
        if parent_id is None:
            raise ValueError(f"Parent '{parent_name}' does not exist.")
        return parent_id

    def _validate_parent(self, node_id: Optional[int], parent_id: Optional[int]) -> None:
        """Reject attaching a node to itself or to one of its own descendants."""
        if parent_id is None or node_id is None:
            return
        if parent_id == node_id:
            raise ValueError("A node cannot be attached to itself.")
        seen = {node_id}
        current: Optional[int] = parent_id
        while current is not None:
            if current in seen:
                raise ValueError("This parent assignment would create a cycle.")
            seen.add(current)
            rel = self.model.get_relationship(current)
            if rel is None:
                break
            current = rel.parent_id

    # ---------------- View events ----------------

    def on_tree_selection_changed(self) -> None:
        node_id = self.view.selected_node_id()
        if node_id is None:
            self.view.set_detail_data(None)
            return
        self.view.set_detail_data(self.model.get_relationship(node_id))

    def on_detail_value_changed(self, field_name: str, new_value: str) -> None:
        node_id = self.view.current_node_id
        if node_id is None:
            return
        if self.model.get_relationship(node_id) is None:
            self.view.show_error(
                "Missing node", f"Node '{self.view.current_entry_name}' no longer exists in the database."
            )
            self.reload_tree()
            return
        try:
            if field_name == self.view.FIELD_ENTRY_NAME:
                new_name = new_value.strip()
                if not new_name:
                    raise ValueError("Entry Name cannot be empty.")
                self.model.rename_relationship(node_id, new_name)
            elif field_name == self.view.FIELD_ATTACHED_TO:
                parent_id = self._resolve_parent(new_value)
                self._validate_parent(node_id, parent_id)
                self.model.update_relationship_field(node_id, "ParentID", parent_id)
            elif field_name == self.view.FIELD_TYPE:
                self.model.update_relationship_field(node_id, "Type", new_value.strip() or None)
            else:
                return
            self.reload_tree(select_node_id=node_id)
        except Exception as exc:
            self.view.show_error("Update failed", str(exc))
            self.view.set_detail_data(self.model.get_relationship(node_id))

    def add_node(self) -> None:
        seed_parent = self.view.selected_entry_name() or ""
        data = RelationshipRow(entry_name="", attached_to=seed_parent, entry_type=None)
        payload = self.view.open_node_dialog(title="Add node", data=data)
        if payload is None:
            return
        try:
            base_name = payload["entry_name"]
            if not base_name:
                raise ValueError("Entry Name cannot be empty.")
            parent_id = self._resolve_parent(payload["attached_to"])
            entry_type = payload["entry_type"]

            if payload["is_multiple"]:
                rows = [
                    RelationshipRow(f"{base_name}_{i}", "", entry_type, parent_id=parent_id)
                    for i in range(1, payload["multiple_count"] + 1)
                ]
                new_ids = self.model.add_multiple_relationships(rows)
                self.reload_tree(select_node_id=new_ids[0] if new_ids else None)
            else:
                new_id = self.model.add_relationship(
                    RelationshipRow(base_name, "", entry_type, parent_id=parent_id)
                )
                self.reload_tree(select_node_id=new_id)
        except Exception as exc:
            self.view.show_error("Add failed", str(exc))

    def edit_node(self) -> None:
        node_id = self.view.selected_node_id()
        if node_id is None:
            self.view.show_warning("No selection", "Select a node first.")
            return
        current = self.model.get_relationship(node_id)
        if current is None:
            self.view.show_error("Missing node", "The selected node no longer exists in the database.")
            self.reload_tree()
            return
        payload = self.view.open_node_dialog(title="Edit node", data=current)
        if payload is None:
            return
        try:
            new_name = payload["entry_name"]
            if not new_name:
                raise ValueError("Entry Name cannot be empty.")
            parent_id = self._resolve_parent(payload["attached_to"])
            self._validate_parent(node_id, parent_id)
            self.model.update_relationship(
                RelationshipRow(new_name, "", payload["entry_type"], node_id=node_id, parent_id=parent_id)
            )
            self.reload_tree(select_node_id=node_id)
        except Exception as exc:
            self.view.show_error("Edit failed", str(exc))

    def delete_node(self) -> None:
        node_id = self.view.selected_node_id()
        if node_id is None:
            self.view.show_warning("No selection", "Select a node first.")
            return
        if not self.view.ask_delete_confirmation(self.view.selected_entry_name()):
            return
        try:
            self.model.delete_relationship(node_id)
            self.reload_tree()
        except Exception as exc:
            self.view.show_error("Delete failed", str(exc))
