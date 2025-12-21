from dataclasses import dataclass
from typing import Optional

@dataclass
class Symbol:
    symbol_id: str
    kind: str  # module, class, function, method
    file: str
    qualname: str
    parent: Optional[str]
    start: int
    docstring: str
    end: int
    hash: str
