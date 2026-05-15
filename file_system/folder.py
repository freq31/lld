

from typing import Dict
from file_system.file_system_entry import FIleSystemEntry, FileSystemEntryType


class Folder(FIleSystemEntry):
    file_system_entries: Dict[str, FIleSystemEntry]
    file_system_entry_type: FileSystemEntryType = FileSystemEntryType.FOLDER

    def __init__(self, parent: Folder, name: str):
        self.parent = parent
        self.name = name
        self.file_system_entries = {}
        self.parent.add(self)

    def get_parent_path(self) -> str:
        return self.parent.get_full_path()

    def get_full_path(self) -> str:
        return f"{self.parent.get_full_path()}/{self.name}" if self.parent else self.name
        
    def add(self, entry: FIleSystemEntry):
        if entry.name in self.file_system_entries:
            raise ValueError(f"Entry with name {entry.name} already exists in folder {self.get_full_path()}")
        self.file_system_entries[entry.name] = entry

    def list(self) -> list[str]:
        return [entry.name for entry in self.file_system_entries.values()]
    
    def list_all(self) -> list[tuple[str, FIleSystemEntry]]:
        entries = []
        for entry in self.file_system_entries.values():
            entries.append((entry.get_full_path(), entry))
            if isinstance(entry, Folder):
                entries.extend(entry.list_all())
        return entries
    
    def rename(self, new_name: str):
        self.parent.rename_entry(self.name, new_name)
        self.name = new_name

    def delete(self):
        self.parent.remove_entry(self.name)
        for entry in self.file_system_entries.values():
            entry.delete()
        self.file_system_entries.clear()

    def move(self, new_parent: Folder):
        self.parent.remove_entry(self.name)
        new_parent.add(self)
        self.parent = new_parent

    def is_descendant(self, folder: Folder, root_folder: Folder) -> bool:
        parent = self.parent
        while parent and parent != root_folder:
            if parent == folder:
                return True
            parent = parent.parent
        return False

    def remove_entry(self, entry_name: str):
        if entry_name not in self.file_system_entries:
            raise ValueError(f"Entry with name {entry_name} does not exist in folder {self.get_full_path()}")
        self.file_system_entries.pop(entry_name)

    def rename_entry(self, old_name: str, new_name: str):
        if old_name not in self.file_system_entries:
            raise ValueError(f"Entry with name {old_name} does not exist in folder {self.get_full_path()}")
        
        if new_name in self.file_system_entries:
            raise ValueError(f"Entry with name {new_name} already exists in folder {self.get_full_path()}")
        
        entry = self.file_system_entries.pop(old_name)
        self.file_system_entries[new_name] = entry
    
    