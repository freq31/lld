from abc import ABC, abstractmethod

class FIleSystemEntry(ABC):
    name: str
    file_system_entry_type: FileSystemEntryType
    
    @abstractmethod
    def rename(self, new_name: str) -> None:
        pass

    @abstractmethod
    def delete(self) -> None:
        pass

    @abstractmethod
    def move(self, new_parent_path: str) -> None:
        pass

    @abstractmethod
    def get_full_path(self) -> str:
        pass



from enum import Enum

class FileSystemEntryType(str, Enum):
    FILE = "file"
    FOLDER = "folder"