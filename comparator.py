import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from scanner import FileInfo


@dataclass
class FileDifference:
    """Représente une différence entre deux fichiers"""
    path: str
    difference_type: str  # 'new', 'modified', 'deleted', 'size_diff', 'hash_diff'
    source_info: Optional[FileInfo] = None
    target_info: Optional[FileInfo] = None
    details: Optional[str] = None


