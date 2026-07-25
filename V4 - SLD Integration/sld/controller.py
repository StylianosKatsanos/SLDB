
# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Dict, List, Optional, Set

from PySide6.QtWidgets import QTreeWidgetItem

from .model import RelationshipRow, SLDModel
from .view import SLDView


class SLDController:
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

    def reload_tree(self, select_entry: Optional[str] = None) -> None:
        relationships = self.model.fetch_relationships()
        self.view.clear_tree()
        parent_map: Dict[str, List[RelationshipRow]] = {}
        root_rows: List[RelationshipRow] = []
        names = {rel.entry_name for rel in relationships}
        for rel in relationships:
            parent_name = (rel.attached_to or "").strip()
            if not parent_name or parent_name == rel.entry_name or parent_name not in names:
                root_rows.append(rel)
            else:
                parent_map.setdefault(parent_name, []).append(rel)

        def add_subtree(parent_item: Optional[QTreeWidgetItem], rel: RelationshipRow, visited: Optional[Set[str]] = None) -> None:
            visited = visited or set()
            if rel.entry_name in visited:
                return
            visited.add(rel.entry_name)
            item = self.view.add_tree_item(parent_item, rel)
            for child in sorted(parent_map.get(rel.entry_name, []), key=lambda x: x.entry_name.lower()):
                add_subtree(item, child, set(visited))

        for root in sorted(root_rows, key=lambda x: x.entry_name.lower()):
            add_subtree(None, root)
        self.view.expand_all()
        if select_entry and self.view.select_entry(select_entry):
            return
        top = self.view.tree.topLevelItem(0)
        if top is not None:
            self.view.tree.setCurrentItem(top)
        else:
            self.view.set_detail_data(None)

    def on_tree_selection_changed(self) -> None:
        entry_name = self.view.selected_entry_name()
        if not entry_name:
            self.view.set_detail_data(None)
            return
        rel = self.model.get_relationship(entry_name)
        self.view.set_detail_data(rel)

    def on_detail_value_changed(self, field_name: str, new_value: str) -> None:
        current_name = self.view.current_entry_name
        if not current_name:
            return
        rel = self.model.get_relationship(current_name)
        if rel is None:
            self.view.show_error("Missing node", f"Node '{current_name}' no longer exists in the database.")
            self.reload_tree()
            return
        try:
            if field_name == self.view.FIELD_ENTRY_NAME:
                new_name = new_value.strip()
                if not new_name:
                    raise ValueError("Entry Name cannot be empty.")
                self.model.rename_relationship(rel.entry_name, new_name)
                self.reload_tree(select_entry=new_name)
                return
            if field_name == self.view.FIELD_ATTACHED_TO:
                self._validate_parent_reference(rel.entry_name, new_value.strip())
                self.model.update_relationship_field(rel.entry_name, "Attached_to", new_value.strip())
                self.reload_tree(select_entry=rel.entry_name)
                return
            if field_name == self.view.FIELD_TYPE:
                self.model.update_relationship_field(rel.entry_name, "Type", new_value.strip() or None)
                self.reload_tree(select_entry=rel.entry_name)
                return
        except Exception as exc:
            self.view.show_error("Update failed", str(exc))
            refreshed = self.model.get_relationship(current_name)
            self.view.set_detail_data(refreshed)

    def _validate_parent_reference(self, entry_name: str, parent_name: str) -> None:
        if not parent_name:
            return
        if parent_name == entry_name:
            raise ValueError("A node cannot be attached to itself.")
        if not self.model.exists(parent_name):
            raise ValueError(f"Parent '{parent_name}' does not exist.")
        seen = {entry_name}
        current = parent_name
        while current:
            if current in seen:
                raise ValueError("This parent assignment would create a cycle.")
            seen.add(current)
            rel = self.model.get_relationship(current)
            if not rel:
                break
            current = (rel.attached_to or "").strip()

    def add_node(self) -> None:
        seed_parent = self.view.selected_entry_name() or ""
        data = RelationshipRow(entry_name="", attached_to=seed_parent, entry_type=None)
        payload = self.view.open_node_dialog(title="Add node", data=data)
        
        if payload is None:
            return
        
        base_name = payload["entry_name"]
        attached_to = payload["attached_to"]
        entry_type = payload["entry_type"]
        is_multiple = payload["is_multiple"]
        multiple_count = payload["multiple_count"]
        
        if not base_name:
            raise ValueError("Entry Name cannot be empty.")
        if self.model.exists(base_name):
            raise ValueError(f"An entry named '{base_name}' already exists.")
        
        self._validate_parent_reference(base_name, attached_to)
        
        try:
            
            if is_multiple:
                rows = [
                    RelationshipRow(
                        entry_name=f"{base_name}_{i}",
                        attached_to=attached_to,
                        entry_type=entry_type,
                    )
                    for i in range(1, multiple_count + 1)
                ]
                self.model.add_multiple_relationships(rows)
                self.reload_tree()
            else:
                row = RelationshipRow(
                    entry_name=base_name, 
                    attached_to=attached_to,
                    entry_type=entry_type,
                )
                self.model.add_relationship(row)
                self.reload_tree(select_entry=base_name)
                
        except Exception as exc:
            self.view.show_error("Add failed", str(exc))

    def edit_node(self) -> None:
        entry_name = self.view.selected_entry_name()
        if not entry_name:
            self.view.show_warning("No selection", "Select a node first.")
            return
        current = self.model.get_relationship(entry_name)
        if current is None:
            self.view.show_error("Missing node", f"Node '{entry_name}' no longer exists in the database.")
            self.reload_tree()
            return
        updated = self.view.open_node_dialog(title="Edit node", data=current)
        if updated is None:
            return
        try:
            if not updated.entry_name:
                raise ValueError("Entry Name cannot be empty.")
            self._validate_parent_reference(updated.entry_name, updated.attached_to)
            self.model.update_relationship(current.entry_name, updated)
            self.reload_tree(select_entry=updated.entry_name)
        except Exception as exc:
            self.view.show_error("Edit failed", str(exc))

    def delete_node(self) -> None:
        entry_name = self.view.selected_entry_name()
        if not entry_name:
            self.view.show_warning("No selection", "Select a node first.")
            return
        if not self.view.ask_delete_confirmation(entry_name):
            return
        try:
            self.model.delete_relationship(entry_name)
            self.reload_tree()
        except Exception as exc:
            self.view.show_error("Delete failed", str(exc))
