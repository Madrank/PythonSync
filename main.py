import argparse
import sys
from pathlib import Path

from file_sync import FileSync
from logger import SyncLogger
from scheduler import SyncScheduler


def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(
        description='Outil de synchronisation de fichiers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  # Synchronisation simple
  python main.py source/ target/ --dry-run
  
  # Synchronisation avec hash
  python main.py source/ target/ --use-hash
  
  # Planification quotidienne
  python main.py source/ target/ --schedule-daily "14:30"
  
  # Planification à intervalle
  python main.py source/ target/ --schedule-interval 60
        """
    )
    
    parser.add_argument('source', type=Path, help='Répertoire source')
    parser.add_argument('target', type=Path, help='Répertoire cible')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Mode simulation (ne modifie rien)')
    parser.add_argument('--use-hash', action='store_true', default=True,
                       help='Utiliser le hash MD5 pour comparaison (par défaut: True)')
    parser.add_argument('--no-hash', dest='use_hash', action='store_false',
                       help='Ne pas utiliser le hash (comparaison par taille/date seulement)')
    
    # Options de planification
    parser.add_argument('--schedule-daily', type=str, metavar='HH:MM',
                       help='Planifier une synchronisation quotidienne à l\'heure spécifiée')
    parser.add_argument('--schedule-hourly', action='store_true',
                       help='Planifier une synchronisation toutes les heures')
    parser.add_argument('--schedule-interval', type=int, metavar='MINUTES',
                       help='Planifier une synchronisation à intervalle régulier (en minutes)')
    parser.add_argument('--schedule-weekly', nargs=2, metavar=('JOUR', 'HH:MM'),
                       help='Planifier une synchronisation hebdomadaire (ex: lundi 14:30)')
    
    args = parser.parse_args()
    
    # Initialisation
    logger = SyncLogger()
    
    try:
        # Créer l'instance de synchronisation
        sync = FileSync(
            source_dir=args.source,
            target_dir=args.target,
            logger=logger,
            use_hash=args.use_hash,
            dry_run=args.dry_run
        )
        
        # Vérifier si planification demandée
        has_schedule = any([
            args.schedule_daily,
            args.schedule_hourly,
            args.schedule_interval,
            args.schedule_weekly
        ])
        
        if has_schedule:
            # Mode planification
            scheduler = SyncScheduler(logger=logger)
            
            def sync_job():
                sync.sync()
            
            if args.schedule_daily:
                scheduler.schedule_daily(args.schedule_daily, sync_job)
            elif args.schedule_hourly:
                scheduler.schedule_hourly(sync_job)
            elif args.schedule_interval:
                scheduler.schedule_interval(args.schedule_interval, sync_job)
            elif args.schedule_weekly:
                scheduler.schedule_weekly(args.schedule_weekly[0], args.schedule_weekly[1], sync_job)
            
            logger.info("Démarrage du planificateur...")
            logger.info("Appuyez sur Ctrl+C pour arrêter")
            
            try:
                scheduler.start(run_in_background=False)
            except KeyboardInterrupt:
                logger.info("\nArrêt demandé par l'utilisateur")
                scheduler.stop()
        else:
            # Mode synchronisation unique
            stats = sync.sync()
            
            print("\n" + "="*50)
            print("RÉSUMÉ DE LA SYNCHRONISATION")
            print("="*50)
            print(f"Fichiers copiés: {stats['copied']}")
            print(f"Fichiers mis à jour: {stats['updated']}")
            print(f"Fichiers supprimés: {stats['deleted']}")
            if stats['errors'] > 0:
                print(f"Erreurs: {stats['errors']}")
                for error in stats['errors_list']:
                    print(f"  - {error}")
            print("="*50)
    
    except KeyboardInterrupt:
        logger.info("\nInterruption par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Erreur fatale: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

