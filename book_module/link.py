from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
from . import node

link_file_name = "link.json"

@dataclass(kw_only=True)
class Link(node.Node):
    point_to: Path
    type: str = 'Link'
    store_file: str = link_file_name
