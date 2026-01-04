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

class FileComparator:
    """Compare deux ensembles de fichiers pour détecter les différences"""
    
    def __init__(self, use_hash: bool = True):
        """
        Initialise le comparateur
        
        Args:
            use_hash: Si True, utilise le hash MD5 pour la comparaison précise
        """
        self.use_hash = use_hash
    
    def calculate_hash(self, file_path: Path, chunk_size: int = 8192) -> str:
        """
        Calcule le hash MD5 d'un fichier
        
        Args:
            file_path: Chemin du fichier
            chunk_size: Taille des chunks pour la lecture
            
        Returns:
            Hash MD5 en hexadécimal
        """
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(chunk_size), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except (IOError, PermissionError) as e:
            raise Exception(f"Impossible de lire le fichier {file_path}: {e}")
    
    def compare_files(self, 
                     source_index: Dict[str, FileInfo],
                     target_index: Dict[str, FileInfo]) -> Dict[str, FileDifference]:
        """
        Compare deux index de fichiers
        
        Args:
            source_index: Index des fichiers source
            target_index: Index des fichiers cible
            
        Returns:
            Dictionnaire des différences {chemin: FileDifference}
        """
        differences = {}
        source_paths = set(source_index.keys())
        target_paths = set(target_index.keys())
        
        # Fichiers nouveaux (présents dans source mais pas dans target)
        new_files = source_paths - target_paths
        for path in new_files:
            differences[path] = FileDifference(
                path=path,
                difference_type='new',
                source_info=source_index[path],
                details=f"Nouveau fichier ({source_index[path].size} octets)"
            )
        
        # Fichiers supprimés (présents dans target mais pas dans source)
        deleted_files = target_paths - source_paths
        for path in deleted_files:
            differences[path] = FileDifference(
                path=path,
                difference_type='deleted',
                target_info=target_index[path],
                details=f"Fichier supprimé ({target_index[path].size} octets)"
            )
        
        # Fichiers communs - vérifier les différences
        common_files = source_paths & target_paths
        for path in common_files:
            source_file = source_index[path]
            target_file = target_index[path]
            
            diff = self._compare_file_pair(source_file, target_file)
            if diff:
                differences[path] = diff
        
        return differences
    
    def _compare_file_pair(self, source_file: FileInfo, target_file: FileInfo) -> Optional[FileDifference]:
        """
        Compare une paire de fichiers
        
        Args:
            source_file: Information du fichier source
            target_file: Information du fichier cible
            
        Returns:
            FileDifference si différences détectées, None sinon
        """
        # Comparaison de taille
        if source_file.size != target_file.size:
            return FileDifference(
                path=source_file.relative_path,
                difference_type='size_diff',
                source_info=source_file,
                target_info=target_file,
                details=f"Taille différente: {source_file.size} vs {target_file.size} octets"
            )
        
        # Comparaison de date de modification
        if abs(source_file.modified_time - target_file.modified_time) > 1.0:  # 1 seconde de tolérance
            # Si les tailles sont identiques mais dates différentes, on peut vérifier le hash
            if self.use_hash:
                try:
                    source_hash = self.calculate_hash(source_file.path)
                    target_hash = self.calculate_hash(target_file.path)
                    
                    if source_hash != target_hash:
                        return FileDifference(
                            path=source_file.relative_path,
                            difference_type='hash_diff',
                            source_info=source_file,
                            target_info=target_file,
                            details=f"Contenu différent (hash: {source_hash[:8]}... vs {target_hash[:8]}...)"
                        )
                    # Même hash mais date différente - probablement copié
                    return FileDifference(
                        path=source_file.relative_path,
                        difference_type='modified',
                        source_info=source_file,
                        target_info=target_file,
                        details=f"Date modifiée (même contenu)"
                    )
                except Exception as e:
                    # Si erreur de hash, on signale juste la différence de date
                    return FileDifference(
                        path=source_file.relative_path,
                        difference_type='modified',
                        source_info=source_file,
                        target_info=target_file,
                        details=f"Date modifiée (impossible de vérifier le hash: {e})"
                    )
            else:
                return FileDifference(
                    path=source_file.relative_path,
                    difference_type='modified',
                    source_info=source_file,
                    target_info=target_file,
                    details=f"Date modifiée"
                )
        
        return None
    
    def get_sync_actions(self, differences: Dict[str, FileDifference]) -> Dict[str, List[str]]:
        """
        Génère la liste des actions de synchronisation à effectuer
        
        Args:
            differences: Dictionnaire des différences
            
        Returns:
            Dictionnaire avec les actions par type
        """
        actions = {
            'copy': [],      # Fichiers à copier
            'delete': [],    # Fichiers à supprimer
            'update': []     # Fichiers à mettre à jour
        }
        
        for diff in differences.values():
            if diff.difference_type == 'new':
                actions['copy'].append(diff.path)
            elif diff.difference_type == 'deleted':
                actions['delete'].append(diff.path)
            elif diff.difference_type in ('modified', 'size_diff', 'hash_diff'):
                actions['update'].append(diff.path)
        
        return actions



