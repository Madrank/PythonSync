import threading
import time
from pathlib import Path
from typing import Callable, Optional

import schedule

from logger import SyncLogger


class SyncScheduler:
    """Planificateur pour automatiser les synchronisations"""
    
    def __init__(self, logger: Optional[SyncLogger] = None):
        """
        Initialise le planificateur
        
        Args:
            logger: Instance du logger (optionnel)
        """
        self.logger = logger or SyncLogger()
        self.running = False
        self.thread: Optional[threading.Thread] = None
    
    def schedule_daily(self, time_str: str, sync_function: Callable):
        """
        Planifie une synchronisation quotidienne
        
        Args:
            time_str: Heure au format "HH:MM" (ex: "14:30")
            sync_function: Fonction à exécuter pour la synchronisation
        """
        schedule.every().day.at(time_str).do(self._wrapper_with_logging, sync_function)
        self.logger.info(f"Synchronisation planifiée quotidiennement à {time_str}")
    
    def schedule_hourly(self, sync_function: Callable):
        """
        Planifie une synchronisation toutes les heures
        
        Args:
            sync_function: Fonction à exécuter pour la synchronisation
        """
        schedule.every().hour.do(self._wrapper_with_logging, sync_function)
        self.logger.info("Synchronisation planifiée toutes les heures")
    
    def schedule_interval(self, minutes: int, sync_function: Callable):
        """
        Planifie une synchronisation à intervalle régulier
        
        Args:
            minutes: Intervalle en minutes
            sync_function: Fonction à exécuter pour la synchronisation
        """
        schedule.every(minutes).minutes.do(self._wrapper_with_logging, sync_function)
        self.logger.info(f"Synchronisation planifiée toutes les {minutes} minutes")
    
    def schedule_weekly(self, day: str, time_str: str, sync_function: Callable):
        """
        Planifie une synchronisation hebdomadaire
        
        Args:
            day: Jour de la semaine ("monday", "tuesday", etc.)
            time_str: Heure au format "HH:MM"
            sync_function: Fonction à exécuter pour la synchronisation
        """
        day_map = {
            'lundi': 'monday',
            'mardi': 'tuesday',
            'mercredi': 'wednesday',
            'jeudi': 'thursday',
            'vendredi': 'friday',
            'samedi': 'saturday',
            'dimanche': 'sunday'
        }
        day_en = day_map.get(day.lower(), day.lower())
        
        getattr(schedule.every(), day_en).at(time_str).do(self._wrapper_with_logging, sync_function)
        self.logger.info(f"Synchronisation planifiée tous les {day} à {time_str}")
    
    def _wrapper_with_logging(self, sync_function: Callable):
        """Wrapper pour ajouter le logging aux fonctions de synchronisation"""
        try:
            self.logger.info("=== Démarrage synchronisation planifiée ===")
            sync_function()
            self.logger.info("=== Synchronisation planifiée terminée ===")
        except Exception as e:
            self.logger.error(f"Erreur lors de la synchronisation planifiée: {e}")
    
    def start(self, run_in_background: bool = True):
        """
        Démarre le planificateur
        
        Args:
            run_in_background: Si True, exécute dans un thread séparé
        """
        if self.running:
            self.logger.warning("Le planificateur est déjà en cours d'exécution")
            return
        
        self.running = True
        
        if run_in_background:
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            self.logger.info("Planificateur démarré en arrière-plan")
        else:
            self.logger.info("Planificateur démarré")
            self._run()
    
    def _run(self):
        """Boucle principale du planificateur"""
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def stop(self):
        """Arrête le planificateur"""
        self.running = False
        schedule.clear()
        self.logger.info("Planificateur arrêté")
    
    def get_pending_jobs(self) -> list:
        """Retourne la liste des tâches planifiées"""
        return schedule.jobs

