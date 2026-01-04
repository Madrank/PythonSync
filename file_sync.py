import shutil
from pathlib import Path
from typing import Optional

from comparator import FileComparator
from logger import SyncLogger
from scanner import FileInfo, FolderScanner


class FileSync:
    """Classe principale pour la synchronisation de fichiers"""
    
    def __init__(self, 
                 source_dir: Path,
                 target_dir: Path,
                 logger: Optional[SyncLogger] = None,
                 use_hash: bool = True,
                 dry_run: bool = False):
        """
        Initialise le synchroniseur
        
        Args:
            source_dir: Répertoire source
            target_dir: Répertoire cible
            logger: Instance du logger (optionnel)
            use_hash: Utiliser le hash pour comparaison précise
            dry_run: Mode simulation (ne fait pas de modifications)
        """
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        self.logger = logger or SyncLogger()
        self.comparator = FileComparator(use_hash=use_hash)
        self.scanner = FolderScanner(exclude_patterns=['.git', '*.tmp', '*.log'])
        self.dry_run = dry_run
        
        if not self.source_dir.exists():
            raise ValueError(f"Le répertoire source n'existe pas: {source_dir}")
        
        self.target_dir.mkdir(parents=True, exist_ok=True)
    
    def scan_source(self) -> dict:
        """Scanne le répertoire source"""
        self.logger.log_scan_start(self.source_dir)
        index = self.scanner.scan_directory(self.source_dir, self.source_dir)
        self.logger.log_scan_complete(
            self.scanner.get_file_count(),
            self.scanner.get_total_size()
        )
        return index
    
    def scan_target(self) -> dict:
        """Scanne le répertoire cible"""
        self.logger.log_scan_start(self.target_dir)
        index = self.scanner.scan_directory(self.target_dir, self.source_dir)
        self.logger.log_scan_complete(
            self.scanner.get_file_count(),
            self.scanner.get_total_size()
        )
        return index
    
    def compare(self, source_index: Optional[dict] = None, target_index: Optional[dict] = None) -> tuple:
        """
        Compare les répertoires source et cible
        
        Args:
            source_index: Index source (scanné si None)
            target_index: Index cible (scanné si None)
            
        Returns:
            Tuple (differences, actions)
        """
        if source_index is None:
            source_index = self.scan_source()
        if target_index is None:
            target_index = self.scan_target()
        
        self.logger.log_comparison_start(self.source_dir, self.target_dir)
        differences = self.comparator.compare_files(source_index, target_index)
        actions = self.comparator.get_sync_actions(differences)
        self.logger.log_comparison_result(differences, actions)
        
        return differences, actions
    
    def sync(self) -> dict:
        """
        Effectue la synchronisation complète
        
        Returns:
            Dictionnaire avec les statistiques de synchronisation
        """
        self.logger.log_sync_start(self.source_dir, self.target_dir)
        
        # Scanner et comparer
        differences, actions = self.compare()
        
        stats = {
            'copied': 0,
            'updated': 0,
            'deleted': 0,
            'errors': 0,
            'errors_list': []
        }
        
        if self.dry_run:
            self.logger.info("MODE SIMULATION - Aucune modification ne sera effectuée")
        
        # Copier les nouveaux fichiers
        for file_path in actions['copy']:
            try:
                source_file = Path(self.source_dir) / file_path
                target_file = Path(self.target_dir) / file_path
                
                if not self.dry_run:
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_file, target_file)
                
                self.logger.log_file_operation("COPIE", file_path)
                stats['copied'] += 1
            except Exception as e:
                error_msg = f"Erreur lors de la copie de {file_path}: {e}"
                self.logger.error(error_msg)
                stats['errors'] += 1
                stats['errors_list'].append(error_msg)
        
        # Mettre à jour les fichiers modifiés
        for file_path in actions['update']:
            try:
                source_file = Path(self.source_dir) / file_path
                target_file = Path(self.target_dir) / file_path
                
                if not self.dry_run:
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_file, target_file)
                
                self.logger.log_file_operation("MISE À JOUR", file_path)
                stats['updated'] += 1
            except Exception as e:
                error_msg = f"Erreur lors de la mise à jour de {file_path}: {e}"
                self.logger.error(error_msg)
                stats['errors'] += 1
                stats['errors_list'].append(error_msg)
        
        # Supprimer les fichiers supprimés dans la source
        for file_path in actions['delete']:
            try:
                target_file = Path(self.target_dir) / file_path
                
                if not self.dry_run:
                    if target_file.exists():
                        target_file.unlink()
                        # Supprimer les répertoires vides
                        try:
                            target_file.parent.rmdir()
                        except OSError:
                            pass  # Le répertoire n'est pas vide
                
                self.logger.log_file_operation("SUPPRESSION", file_path)
                stats['deleted'] += 1
            except Exception as e:
                error_msg = f"Erreur lors de la suppression de {file_path}: {e}"
                self.logger.error(error_msg)
                stats['errors'] += 1
                stats['errors_list'].append(error_msg)
        
        self.logger.log_sync_complete(
            stats['copied'],
            stats['updated'],
            stats['deleted'],
            stats['errors'],
            dry_run=self.dry_run
        )
        
        # Sauvegarder le rapport
        report = {
            'source': str(self.source_dir),
            'target': str(self.target_dir),
            'stats': stats,
            'differences_count': len(differences),
            'dry_run': self.dry_run
        }
        self.logger.save_sync_report(report)
        
        return stats

