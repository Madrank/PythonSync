import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
import json


class SyncLogger:
    """Gestionnaire de logs pour les opérations de synchronisation"""
    
    def __init__(self, log_dir: Path = Path("logs"), log_level: int = logging.INFO):
        """
        Initialise le logger
        
        Args:
            log_dir: Répertoire pour les fichiers de logs
            log_level: Niveau de logging (logging.DEBUG, INFO, WARNING, ERROR)
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Configuration du logger Python
        self.logger = logging.getLogger('FileSync')
        self.logger.setLevel(log_level)
        
        # Éviter les doublons de handlers
        if not self.logger.handlers:
            # Handler pour fichier
            log_file = self.log_dir / f"sync_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(log_level)
            
            # Handler pour console
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            
            # Format
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def info(self, message: str):
        """Log niveau INFO"""
        self.logger.info(message)
    
    def debug(self, message: str):
        """Log niveau DEBUG"""
        self.logger.debug(message)
    
    def warning(self, message: str):
        """Log niveau WARNING"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log niveau ERROR"""
        self.logger.error(message)
    
    def log_scan_start(self, directory: Path):
        """Log le début d'un scan"""
        self.info(f"Début du scan: {directory}")
    
    def log_scan_complete(self, file_count: int, total_size: int):
        """Log la fin d'un scan"""
        size_mb = total_size / (1024 * 1024)
        self.info(f"Scan terminé: {file_count} fichiers ({size_mb:.2f} MB)")
    
    def log_comparison_start(self, source: Path, target: Path):
        """Log le début d'une comparaison"""
        self.info(f"Début comparaison: {source} -> {target}")
    
    def log_comparison_result(self, differences: dict, actions: dict):
        """Log les résultats d'une comparaison"""
        total_diffs = len(differences)
        copy_count = len(actions.get('copy', []))
        update_count = len(actions.get('update', []))
        delete_count = len(actions.get('delete', []))
        
        self.info(f"Comparaison terminée: {total_diffs} différences trouvées")
        self.info(f"  - À copier: {copy_count}")
        self.info(f"  - À mettre à jour: {update_count}")
        self.info(f"  - À supprimer: {delete_count}")
    
    def log_sync_start(self, source: Path, target: Path):
        """Log le début d'une synchronisation"""
        self.info(f"Début synchronisation: {source} -> {target}")
    
    def log_sync_complete(self, copied: int, updated: int, deleted: int, errors: int, dry_run: bool = False):
        """Log la fin d'une synchronisation"""
        if dry_run:
            self.info(f"Synchronisation terminée (MODE SIMULATION):")
            self.info(f"  - Seraient copiés: {copied}")
            self.info(f"  - Seraient mis à jour: {updated}")
            self.info(f"  - Seraient supprimés: {deleted}")
        else:
            self.info(f"Synchronisation terminée:")
            self.info(f"  - Copiés: {copied}")
            self.info(f"  - Mis à jour: {updated}")
            self.info(f"  - Supprimés: {deleted}")
        if errors > 0:
            self.warning(f"  - Erreurs: {errors}")
    
    def log_file_operation(self, operation: str, file_path: str, status: str = "succès"):
        """Log une opération sur un fichier"""
        self.debug(f"{operation}: {file_path} - {status}")
    
    def save_sync_report(self, report_data: dict, filename: Optional[str] = None):
        """
        Sauvegarde un rapport de synchronisation en JSON
        
        Args:
            report_data: Données du rapport
            filename: Nom du fichier (optionnel, généré automatiquement si None)
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"sync_report_{timestamp}.json"
        
        report_file = self.log_dir / filename
        report_data['timestamp'] = datetime.now().isoformat()
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
            self.info(f"Rapport sauvegardé: {report_file}")
        except Exception as e:
            self.error(f"Impossible de sauvegarder le rapport: {e}")

