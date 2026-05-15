
from typing import Dict
from file_system.file import File
from file_system.folder import Folder


class FileSystemManager:
    file_entries: Dict[str, File]
    folder_entries: Dict[str, Folder]
    root_folder_path: str = "G:/"

    def __init__(self):
        root_folder = Folder("", "G:/")
        self.file_entries = {}
        self.folder_entries = {}
        self.folder_entries[root_folder.get_full_path()] = root_folder

    def create_file(self, parent_folder_path: str, name: str, content: str) -> File:
        file_path = f"{parent_folder_path}/{name}"
        if file_path in self.file_entries:
            raise ValueError(f"File with name {name} already exists in folder {parent_folder_path}")
        
        if file_path in self.folder_entries:
            raise ValueError(f"Folder with name {name} already exists in folder {parent_folder_path}")
        
        parent_path = f"{parent_folder_path}"
        if parent_path not in self.folder_entries:
            raise ValueError(f"Parent folder {parent_folder_path} does not exist")
        
        parent_folder = self.folder_entries[parent_path]
        new_file = File(parent_folder, name, content)
        self.file_entries[file_path] = new_file
        return new_file
    
    def create_folder(self, parent_folder_path: str, name: str) -> Folder:
        folder_path = f"{parent_folder_path}/{name}"
        if folder_path in self.file_entries:
            raise ValueError(f"File with name {name} already exists in folder {parent_folder_path}")
        
        if folder_path in self.folder_entries:
            raise ValueError(f"Folder with name {name} already exists in folder {parent_folder_path}")
        
        parent_path = f"{parent_folder_path}"
        if parent_path not in self.folder_entries:
            raise ValueError(f"Parent folder {parent_folder_path} does not exist")
        
        parent_folder = self.folder_entries[parent_path]
        new_folder = Folder(parent_folder, name)
        self.folder_entries[folder_path] = new_folder
        return new_folder
    

    def list_folder(self, folder_path: str) -> list[str]:
        if folder_path not in self.folder_entries:
            raise ValueError(f"Folder {folder_path} does not exist")
        
        folder = self.folder_entries[folder_path]
        return folder.list()
    
    def get_file_content(self, file_path: str) -> str:
        if file_path not in self.file_entries:
            raise ValueError(f"File {file_path} does not exist")
        
        file = self.file_entries[file_path]
        return file.read()
    
    def update_file_content(self, file_path: str, new_content: str) -> None:
        if file_path not in self.file_entries:
            raise ValueError(f"File {file_path} does not exist")
        
        file = self.file_entries[file_path]
        file.update(new_content)

    def delete_file(self, file_path: str) -> None:
        if file_path not in self.file_entries:
            raise ValueError(f"File {file_path} does not exist")
        
        file = self.file_entries[file_path]
        
        file.delete()
        self.file_entries.pop(file_path, None)

    def delete_folder(self, folder_path: str) -> None:
        if folder_path not in self.folder_entries:
            raise ValueError(f"Folder {folder_path} does not exist")
        
        if folder_path == self.root_folder_path:
            raise ValueError("Cannot delete root folder")

        folder= self.folder_entries[folder_path]
        
        child_file_system_entries = folder.list_all()
        for entry_path, entry in child_file_system_entries:
            if entry_path in self.file_entries:
                self.file_entries.pop(entry_path, None)
            elif entry_path in self.folder_entries:
                self.folder_entries.pop(entry_path, None)
        
        folder.delete()
        self.folder_entries.pop(folder_path, None)

    def rename_file(self, file_path: str, new_name: str) -> File:
        if file_path not in self.file_entries:
            raise ValueError(f"File {file_path} does not exist")
        
        file = self.file_entries[file_path]
       
        file.rename(new_name)
        self.file_entries.pop(file_path, None)
        self.file_entries[file.get_full_path()] = file
        return file

    def rename_folder(self, folder_path: str, new_name: str) -> Folder:
        if folder_path not in self.folder_entries:
            raise ValueError(f"Folder {folder_path} does not exist")
        
        if folder_path == self.root_folder_path:
            raise ValueError("Cannot rename the root folder")

        folder= self.folder_entries[folder_path]

        new_folder_path = folder.get_parent_path()+ "/"+ new_name
        if new_folder_path in self.folder_entries or new_folder_path in self.file_entries:
            raise ValueError("Already Exists")

        child_file_system_entries = folder.list_all()
        for entry_path, entry in child_file_system_entries:
            if entry_path in self.file_entries:
                self.file_entries.pop(entry_path, None)
            elif entry_path in self.folder_entries:
                self.folder_entries.pop(entry_path, None)

        folder.rename(new_name)
        self.folder_entries.pop(folder_path, None)

        child_file_system_entries = folder.list_all()
        for entry_path, entry in child_file_system_entries:
            if isinstance(entry, File):
                self.file_entries[entry_path] = entry
            elif isinstance(entry, Folder):
                self.folder_entries[entry_path] = entry

        self.folder_entries[folder.get_full_path()] = folder
        return folder

    def move_file(self, file_path: str, new_parent_path: str) -> File:
        if file_path not in self.file_entries:
            raise ValueError(f"File {file_path} does not exist")
        
        file = self.file_entries[file_path]
        if new_parent_path not in self.folder_entries:
            raise ValueError(f"New parent folder {new_parent_path} does not exist")
        
        new_parent_folder = self.folder_entries[new_parent_path]
        file.move(new_parent_folder)
        self.file_entries.pop(file_path, None)
        self.file_entries[file.get_full_path()] = file
        return file

    def move_folder(self, folder_path: str, new_parent_path: str) -> Folder:
        if folder_path not in self.folder_entries:
            raise ValueError(f"Folder {folder_path} does not exist")
        
        if folder_path == self.root_folder_path:
            raise ValueError("Cannot move the root folder")
        
        folder= self.folder_entries[folder_path]
        
        if new_parent_path not in self.folder_entries:
            raise ValueError(f"New parent folder {new_parent_path} does not exist")
        
        new_parent_folder = self.folder_entries[new_parent_path]

        if new_parent_folder.is_descendant(folder, self.folder_entries[self.root_folder_path]):
            raise ValueError("Cannot move a folder inside its own subfolder")

        child_file_system_entries = folder.list_all()
        for entry_path, entry in child_file_system_entries:
            if entry_path in self.file_entries:
                self.file_entries.pop(entry_path, None)
            elif entry_path in self.folder_entries:
                self.folder_entries.pop(entry_path, None)
        
        folder.move(new_parent_folder)
        self.folder_entries.pop(folder_path, None)

        child_file_system_entries = folder.list_all()
        for entry_path, entry in child_file_system_entries:
            if isinstance(entry, File):
                self.file_entries[entry_path] = entry
            elif isinstance(entry, Folder):
                self.folder_entries[entry_path] = entry
        self.folder_entries[folder.get_full_path()] = folder
        return folder

        
