# Outil de Synchronisation de Fichiers

Outil de synchronisation de fichiers en Python avec scan de dossiers, comparaison de fichiers, logs et planification.

## Fonctionnalités

- ✅ **Scan de dossiers** : Parcours récursif et indexation des fichiers
- ✅ **Comparaison de fichiers** : Par taille, date de modification et hash MD5
- ✅ **Logs** : Journalisation complète des opérations et rapports JSON
- ✅ **Planification** : Synchronisations automatiques (quotidienne, horaire, intervalle, hebdomadaire)
- ✅ **Mode simulation** : Test sans modification (dry-run)

## Installation

1. Assurez-vous d'avoir Python 3.7+ installé

2. Installez les dépendances :

```bash
pip install -r requirements.txt
```

## Utilisation

> 💡 **Nouveau :** Consultez le [GUIDE_UTILISATION.md](GUIDE_UTILISATION.md) pour un guide complet d'utilisation en ligne de commande (sans IDE).

### Syntaxe de base

```bash
python main.py <source> <target> [options]
```

- `<source>` : Répertoire source à synchroniser
- `<target>` : Répertoire cible de destination

### Options disponibles

- `--dry-run` : Mode simulation (affiche ce qui serait fait sans modifier)
- `--use-hash` : Utilise le hash MD5 pour comparaison précise (par défaut)
- `--no-hash` : Désactive le hash (comparaison par taille/date seulement)

### Options de planification

- `--schedule-daily HH:MM` : Synchronisation quotidienne à l'heure spécifiée
- `--schedule-hourly` : Synchronisation toutes les heures
- `--schedule-interval MINUTES` : Synchronisation à intervalle régulier
- `--schedule-weekly JOUR HH:MM` : Synchronisation hebdomadaire

## Exemples d'utilisation

### 1. Synchronisation simple (mode simulation)

Testez d'abord avec le mode simulation pour voir ce qui sera synchronisé :

```bash
python main.py C:\Users\MonUser\Documents C:\Backup\Documents --dry-run
```

### 2. Synchronisation réelle

Effectue la synchronisation complète :

```bash
python main.py C:\Users\MonUser\Documents C:\Backup\Documents
```

### 3. Synchronisation quotidienne

Synchronise tous les jours à 14h30 :

```bash
python main.py C:\Users\MonUser\Documents C:\Backup\Documents --schedule-daily "14:30"
```

Appuyez sur `Ctrl+C` pour arrêter le planificateur.

### 4. Synchronisation toutes les heures

```bash
python main.py C:\Users\MonUser\Documents C:\Backup\Documents --schedule-hourly
```

### 5. Synchronisation toutes les 30 minutes

```bash
python main.py C:\Users\MonUser\Documents C:\Backup\Documents --schedule-interval 30
```

### 6. Synchronisation hebdomadaire

Synchronise tous les lundis à 9h00 :

```bash
python main.py C:\Users\MonUser\Documents C:\Backup\Documents --schedule-weekly lundi "09:00"
```

Jours disponibles : `lundi`, `mardi`, `mercredi`, `jeudi`, `vendredi`, `samedi`, `dimanche`

## Structure des fichiers

```
.
├── main.py              # Interface en ligne de commande
├── file_sync.py         # Moteur de synchronisation principal
├── scanner.py           # Module de scan de dossiers
├── comparator.py        # Module de comparaison de fichiers
├── logger.py            # Module de logging
├── scheduler.py         # Module de planification
├── requirements.txt     # Dépendances Python
└── logs/                # Dossier des logs (créé automatiquement)
    ├── sync_YYYYMMDD.log       # Fichiers de logs journaliers
    └── sync_report_YYYYMMDD_HHMMSS.json  # Rapports de synchronisation
```

## Fonctionnement

1. **Scan** : L'outil scanne récursivement les répertoires source et cible
2. **Comparaison** : Les fichiers sont comparés par taille, date et hash MD5
3. **Synchronisation** :
   - Copie les nouveaux fichiers
   - Met à jour les fichiers modifiés
   - Supprime les fichiers absents de la source
4. **Logs** : Toutes les opérations sont enregistrées dans les logs

## Fichiers exclus automatiquement

Par défaut, les patterns suivants sont exclus :

- Dossiers cachés (commençant par `.`)
- Fichiers `.git`
- Fichiers temporaires `*.tmp`
- Fichiers de logs `*.log`

## Logs et rapports

- **Logs journaliers** : `logs/sync_YYYYMMDD.log`
- **Rapports JSON** : `logs/sync_report_YYYYMMDD_HHMMSS.json`

Les rapports contiennent :

- Statistiques de synchronisation
- Liste des différences détectées
- Erreurs éventuelles
- Horodatage

## Exemple de sortie

```
2024-01-15 14:30:00 - FileSync - INFO - Début du scan: C:\Users\MonUser\Documents
2024-01-15 14:30:02 - FileSync - INFO - Scan terminé: 150 fichiers (45.32 MB)
2024-01-15 14:30:02 - FileSync - INFO - Début comparaison: C:\Users\MonUser\Documents -> C:\Backup\Documents
2024-01-15 14:30:05 - FileSync - INFO - Comparaison terminée: 12 différences trouvées
2024-01-15 14:30:05 - FileSync - INFO -   - À copier: 5
2024-01-15 14:30:05 - FileSync - INFO -   - À mettre à jour: 7
2024-01-15 14:30:05 - FileSync - INFO -   - À supprimer: 0

==================================================
RÉSUMÉ DE LA SYNCHRONISATION
==================================================
Fichiers copiés: 5
Fichiers mis à jour: 7
Fichiers supprimés: 0
==================================================
```

## Dépannage

### Erreur de permissions

Assurez-vous d'avoir les droits d'écriture sur le répertoire cible.

### Fichiers verrouillés

Certains fichiers peuvent être verrouillés par d'autres applications. L'outil les signale dans les logs.

### Chemin avec espaces

Sur Windows, utilisez des guillemets si vos chemins contiennent des espaces :

```bash
python main.py "C:\Mes Documents" "C:\Backup\Mes Documents"
```

## Dépendances

- `schedule` : Bibliothèque de planification de tâches

## Licence

Projet libre d'utilisation.
