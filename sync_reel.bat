@echo off
chcp 65001 >nul
echo ========================================
echo  Outil de Synchronisation de Fichiers
echo  MODE REEL (modifications effectuées)
echo ========================================
echo.
echo ATTENTION: Cette synchronisation va modifier les fichiers!
echo.
pause

REM Configuration - MODIFIEZ CES CHEMINS SELON VOS BESOINS
set SOURCE=C:\Users\Madrank\Documents
set TARGET=C:\Users\Madrank\Pictures\Backup

echo Source: %SOURCE%
echo Cible: %TARGET%
echo.
python main.py "%SOURCE%" "%TARGET%"

echo.
echo ========================================
echo Synchronisation terminée!
echo ========================================
pause

