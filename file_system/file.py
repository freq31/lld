
from file_system.file_system_entry import FIleSystemEntry, FileSystemEntryType
from file_system.folder import Folder


class File(FIleSystemEntry):
    file_system_entry_type: FileSystemEntryType = FileSystemEntryType.FILE
    
    def __init__(self, parent: Folder, name: str, content: str):
        self.parent = parent
        self.name = name
        self.content = content
        parent.add(self)

    def update(self, new_content: str):
        self.content = new_content

    def read(self) -> str:
        return self.content

    def rename(self, new_name: str):
        self.parent.rename_entry(self.name, new_name)
        self.name = new_name

    def delete(self):
        self.content = ""
        self.parent.remove_entry(self.name)

    def move(self, new_parent: Folder):
        self.parent.remove_entry(self.name)
        new_parent.add(self)

    def get_parent_path(self) -> str:
        return self.parent.get_full_path()
    
    def get_full_path(self) -> str:
        return f"{self.parent.get_full_path()}/{self.name}"