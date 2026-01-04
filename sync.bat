@echo off
chcp 65001 >nul
echo ========================================
echo  Outil de Synchronisation de Fichiers
echo ========================================
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Python n'est pas installé ou pas dans le PATH
    echo Essayez avec: py --version
    pause
    exit /b 1
)

REM Vérifier si les dépendances sont installées
python -c "import schedule" >nul 2>&1
if errorlevel 1 (
    echo Installation des dépendances...
    python -m pip install -r requirements.txt
    echo.
)

REM Configuration - MODIFIEZ CES CHEMINS SELON VOS BESOINS
set SOURCE=C:\Users\Madrank\Documents
set TARGET=C:\Users\Madrank\Pictures\Backup

echo Source: %SOURCE%
echo Cible: %TARGET%
echo.
echo Mode: SIMULATION (dry-run)
echo.
echo ATTENTION: En mode simulation, aucun fichier ne sera réellement copié!
echo.
pause

REM Lancer la synchronisation en mode simulation
python main.py "%SOURCE%" "%TARGET%" --dry-run

echo.
echo ========================================
echo Synchronisation terminée!
echo ========================================
pause

