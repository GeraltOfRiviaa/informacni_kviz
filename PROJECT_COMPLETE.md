# Stav Projektu

## Celkový stav

Projekt je ve stavu funkční aplikace s aktivním administračním modulem, herní logikou a GUI. Probíhají průběžné úpravy UX a obsahových dat pro ostrou soutěž.

## Co je hotovo

- datové modely (`models/`)
- herní orchestrace (`app/`, `services/round_manager.py`)
- bodování, systém nápověd, časovač
- kontrola odpovědí přes hash + salt
- autentizace správce a správa otázek
- upload a validace obrázků
- načítání obrázků z `assets/images/` (normální soubory)
- zástupný obrázek při chybějícím souboru

## Nedávné změny

- odstraněna závislost na `assets/images_archive.zip`
- `prepare_questions.py` přepsán na plain-file pipeline
- `config.py` přepnuto na `images_dir = assets/images`
- `ui/round_screen.py` zlepšené vizuální rozvržení a robustnější zobrazování obrázků
- hlavní dokumentace přepsána podle aktuálního stavu projektu

## Známé limity

- repozitář může být bez reálných produkčních obrázků
- část GUI testů může být závislá na dostupnosti Tk prostředí

## Doporučení před soutěží

1. Naplnit `original_data/images/` reálnými obrázky.
2. Spustit `python prepare_questions.py`.
3. Spustit testy a smoke test GUI.
4. Změnit výchozí heslo správce.
5. Projít `PRE_DEPLOYMENT_CHECKLIST.md`.
