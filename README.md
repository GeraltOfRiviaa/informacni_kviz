# Informační Kvíz

Desktop aplikace v Pythonu (Tkinter) pro školní týmovou soutěž s obrázkovými otázkami.

## Co aplikace umí

- Herní režim s odhalováním obrázku v mřížce 4x4.
- Bodování s penalizací za odhalená pole, nápovědy a špatné odpovědi.
- Admin režim pro správu otázek a obrázků.
- Ukládání otázek v bezpečném tvaru (hash + salt, bez plaintext odpovědi).
- Lokální běh bez potřeby internetu.

## Technologie

- Python 3.8+
- Tkinter (GUI)
- Pillow (práce s obrázky)
- Cryptography (bezpečnostní část)
- PyInstaller (build distribuce)

## Struktura projektu

- `main.py` - vstupní bod aplikace
- `gui.py` - přepínání obrazovek a orchestrátor GUI
- `ui/` - obrazovky aplikace
- `services/` - herní logika, práce s daty, bezpečnost
- `models/` - datové modely
- `data/questions.json` - runtime otázky (hashované)
- `original_data/questions_input.json` - vstupní otázky pro přípravu
- `original_data/images/` - vstupní obrázky
- `assets/images/` - runtime obrázky

## Lokální spuštění

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Příprava otázek

Pokud pracuješ se vstupními daty (`original_data`), použij:

```bash
python prepare_questions.py
```

Tím se vytvoří/aktualizuje `data/questions.json` a runtime obrázky v `assets/images/`.

## Build na Windows (.exe)

### Standardní distribuce (doporučeno)

Jeden příkaz:

```bash
py build_exe.py
```

Výstup:

- `dist/informacni_kviz/`
- `dist/informacni_kviz_v1.0.zip`

### Jeden samostatný exe build

```bash
py build_exe.py --onefile
```

Skript vytvoří balíček v `dist/informacni_kviz/` obsahující jeden `informacni_kviz.exe` a doprovodné soubory.

## Bezpečnostní poznámka

`data/questions.json` neobsahuje plaintext správných odpovědí. Ověření probíhá porovnáním hashů po normalizaci vstupu.

## Dokumentace

- [ADMIN_GUIDE.md](ADMIN_GUIDE.md)
- [SECURITY_FAQ.md](SECURITY_FAQ.md)
- [docs/design.md](docs/design.md)
- [docs/user_guide.md](docs/user_guide.md)
