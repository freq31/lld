from dataclasses import dataclass

@dataclass(frozen=True)
class Product:
    Id: str
    name: str