# 🚀 Guide Complet: Convertir Python en EXE

## 📋 Prérequis

- Python 3.7+ installé
- Ton fichier `temp.py` dans le même dossier
- Les dépendances installées

---

## ✅ Étape 1: Installer les dépendances

### Ouvrir CMD ou PowerShell dans le dossier du projet:

```bash
pip install -r requirements.txt
```

**Ou manuellement:**

```bash
pip install numpy matplotlib networkx pyinstaller
```

---

## 🔨 Étape 2: Convertir en EXE

### Méthode 1: Utiliser le script automatisé (RECOMMANDÉ)

```bash
python build_exe.py
```

### Méthode 2: Commande PyInstaller directe

```bash
pyinstaller --onefile --windowed temp.py
```

---

## 📂 Résultats

Après la conversion, tu trouveras:

```
📁 projet/
├── dist/
│   └── PartieITI.exe  ← 🎯 TON FICHIER EXÉCUTABLE!
├── build/
├── temp.spec
├── temp.py
├── build_exe.py
└── requirements.txt
```

---

## 🎯 Utiliser l'EXE

### Lancer l'application:
- Double-clic sur `dist/PartieITI.exe`
- Ou exécuter depuis CMD: `dist\PartieITI.exe`

### Partager l'application:
- Tu peux copier le fichier `dist/PartieITI.exe` seul
- Ou partager tout le dossier `dist/`

---

## ⚙️ Options PyInstaller avancées

| Option | Description |
|--------|-------------|
| `--onefile` | Un seul fichier .exe |
| `--windowed` | Pas de fenêtre console |
| `--icon=app.ico` | Ajouter une icône personnalisée |
| `--name=MyApp` | Renommer l'application |
| `--add-data "src:dest"` | Inclure des fichiers ressources |

### Exemple avec icône:
```bash
pyinstaller --onefile --windowed --icon=app.ico temp.py
```

---

## 🐛 Dépannage

### Erreur: "pyinstaller not found"
```bash
pip install pyinstaller
```

### Erreur: "Module not found"
```bash
pyinstaller --onefile --windowed --hidden-import=tkinter temp.py
```

### L'EXE ne s'ouvre pas
- Vérifie que toutes les dépendances sont installées
- Lance depuis CMD pour voir les erreurs:
  ```bash
  dist\PartieITI.exe
  ```

---

## 📊 Tailles typiques

| Type | Taille |
|------|--------|
| EXE seul (--onefile) | 50-150 MB |
| Dossier dist/ | 200-400 MB |

---

## 💡 Conseils

✅ **Avant la conversion:**
- Teste ton application Python en local
- Assure-toi que tout fonctionne

✅ **Après la conversion:**
- Teste l'EXE sur un autre PC (si possible)
- Crée un raccourci pour accès rapide
- Archive le dossier `dist/` pour distribution

---

## 📖 Pour plus d'infos

- [Documentation PyInstaller](https://pyinstaller.org/)
- [Python Packaging Guide](https://packaging.python.org/)

---

**Besoin d'aide?** Regarde les fichiers `requirements.txt` et `build_exe.py` dans ce repo! 🎉
