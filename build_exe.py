#!/usr/bin/env python3
"""
Script de conversion Python .py vers .exe
Utilise PyInstaller pour créer un exécutable Windows standalone
"""

import os
import sys
import subprocess

def build_exe():
    """
    Convertit le fichier Python en .exe
    """
    print("=" * 70)
    print("🚀 CONVERSION PYTHON TO EXE - PartieITI Application")
    print("=" * 70)
    
    # Nom du fichier Python principal
    python_file = "temp.py"
    
    # Vérifier que le fichier existe
    if not os.path.exists(python_file):
        print(f"❌ ERREUR: Le fichier '{python_file}' n'existe pas!")
        print(f"📁 Fichiers dans le répertoire courant:")
        for f in os.listdir("."):
            print(f"   - {f}")
        sys.exit(1)
    
    print(f"\n✅ Fichier trouvé: {python_file}")
    
    # Commande PyInstaller
    cmd = [
        "pyinstaller",
        "--onefile",           # Un seul fichier .exe
        "--windowed",          # Sans fenêtre console
        "--name=PartieITI",   # Nom de l'application
        "--icon=ICON.ico" if os.path.exists("ICON.ico") else "",  # Icône (optionnelle)
        python_file
    ]
    
    # Filtrer les commandes vides
    cmd = [c for c in cmd if c]
    
    print("\n" + "=" * 70)
    print("📦 Commande PyInstaller:")
    print(" ".join(cmd))
    print("=" * 70)
    
    try:
        # Exécuter PyInstaller
        print("\n⏳ Conversion en cours... (cela peut prendre quelques minutes)")
        result = subprocess.run(cmd, check=True)
        
        print("\n" + "=" * 70)
        print("✅ CONVERSION RÉUSSIE!")
        print("=" * 70)
        print("\n📍 Fichier .exe créé à:")
        exe_path = os.path.join("dist", "PartieITI.exe")
        print(f"   {os.path.abspath(exe_path)}")
        print("\n🎯 Tu peux maintenant:")
        print(f"   1. Double-cliquer sur: dist/PartieITI.exe")
        print(f"   2. Partager le dossier 'dist' avec d'autres")
        print(f"   3. Créer un raccourci vers l'exécutable")
        print("\n📁 Fichiers générés:")
        print("   - dist/PartieITI.exe (ton application exécutable)")
        print("   - build/ (fichiers intermédiaires)")
        print("   - PartieITI.spec (configuration PyInstaller)")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ ERREUR lors de la conversion: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("\n❌ ERREUR: PyInstaller n'est pas installé!")
        print("\n📋 Pour installer PyInstaller, exécute:")
        print("   pip install pyinstaller")
        sys.exit(1)

if __name__ == "__main__":
    build_exe()
