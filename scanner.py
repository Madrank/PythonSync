"""
Module de scan de dossiers pour l'outil de synchronisation
"""
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class FileInfo:
    """Informations sur un fichier"""
    path: Path
    size: int
    modified_time: float
    hash_value: Optional[str] = None
    
    @property
    def relative_path(self) -> str:
        """Chemin relatif du fichier"""
        return str(self.path)
    
    @property
    def modified_datetime(self) -> datetime:
        """Date de modification en datetime"""
        return datetime.fromtimestamp(self.modified_time)


class FolderScanner:
    """Scanner de dossiers pour lister et indexer les fichiers"""
    
    def __init__(self, exclude_patterns: Optional[List[str]] = None):
        """
        Initialise le scanner
        
        Args:
            exclude_patterns: Liste de patterns à exclure (ex: ['*.tmp', '.git'])
        """
        self.exclude_patterns = exclude_patterns or []
        self._file_index: Dict[str, FileInfo] = {}
    
    def should_exclude(self, path: Path) -> bool:
        """Vérifie si un chemin doit être exclu"""
        path_str = str(path)
        for pattern in self.exclude_patterns:
            if pattern in path_str or path.name.startswith('.'):
                return True
        return False
    
    def scan_directory(self, directory: Path, base_path: Optional[Path] = None) -> Dict[str, FileInfo]:
        """
        Scanne un répertoire récursivement
        
        Args:
            directory: Chemin du répertoire à scanner
            base_path: Chemin de base pour les chemins relatifs (optionnel)
            
        Returns:
            Dictionnaire {chemin_relatif: FileInfo}
        """
        if base_path is None:
            base_path = directory
        
        file_index = {}
        
        if not directory.exists():
            return file_index
        
        try:
            for root, dirs, files in os.walk(directory):
                # Filtrer les dossiers à exclure
                dirs[:] = [d for d in dirs if not self.should_exclude(Path(root) / d)]
                
                for file in files:
                    file_path = Path(root) / file
                    
                    if self.should_exclude(file_path):
                        continue
                    
                    try:
                        stat = file_path.stat()
                        relative_path = str(file_path.relative_to(base_path))
                        
                        file_info = FileInfo(
                            path=file_path,
                            size=stat.st_size,
                            modified_time=stat.st_mtime
                        )
                        
                        file_index[relative_path] = file_info
                    except (OSError, PermissionError) as e:
                        # Ignorer les fichiers inaccessibles
                        continue
        
        except Exception as e:
            print(f"Erreur lors du scan de {directory}: {e}")
        
        self._file_index = file_index
        return file_index
    
    def get_file_count(self) -> int:
        """Retourne le nombre de fichiers indexés"""
        return len(self._file_index)
    
    def get_total_size(self) -> int:
        """Retourne la taille totale des fichiers indexés"""
        return sum(f.size for f in self._file_index.values())
    
    def get_file_index(self) -> Dict[str, FileInfo]:
        """Retourne l'index des fichiers"""
        return self._file_index.copy()

