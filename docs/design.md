# Architektura Aplikace

Tento dokument popisuje aktuální stav architektury projektu `informacni_kviz`.

## 1. Účel aplikace

Desktopová aplikace pro školní soutěžní kolo, kde tým odhaluje obrázek po částech (mřížka 4x4), sbírá nápovědy a hádá odpověď pod časovým limitem.

## 2. Technologický základ

- Python 3.8+
- Tkinter GUI
- Pillow (PIL) pro obrázky
- JSON datové soubory
- `pytest` pro testy

## 3. Vrstvy aplikace

### Prezentační vrstva (`ui/`, část `gui.py`)

- `ui/round_screen.py`: hlavní herní obrazovka
- `ui/admin_*`: obrazovky pro administraci
- `gui.py`: orchestruje přepínání obrazovek a tok hry

### Aplikační/logická vrstva (`services/`, část `app/`)

- `services/round_manager.py`: řídí jedno kolo
- `services/score_manager.py`: bodování a penalizace
- `services/timer_service.py`: odpočet času
- `services/hint_system.py`: nápovědy
- `services/answer_checker.py`: kontrola odpovědí
- `services/image_handler.py`: načítání a příprava obrázků

### Datová vrstva (`models/`, `data/`)

- `models/`: datové třídy (`Question`, `Team`, `GameState`, ...)
- `data/questions.json`: otázky bez plaintext odpovědí
- `data/config.json`: konfigurace běhu

## 4. Bezpečnost odpovědí

- Odpovědi nejsou uložené jako plaintext
- Používá se hash + salt (`answer_hash`, `answer_salt`)
- Ověření odpovědi probíhá porovnáním hashe po normalizaci vstupu

## 5. Obrázky a obsah

- Runtime obrázky se čtou z `assets/images/`
- Obrázky už nejsou zabalené v ZIP archivu
- Přípravu dat provádí `prepare_questions.py` z `original_data/`

## 6. Herní tok (zjednodušeně)

1. Načtení otázky podle režimu/obtížnosti
2. Spuštění kola (`RoundManager` + `RoundScreen`)
3. Odhalování buněk, nápovědy, penalizace
4. Odeslání odpovědi a vyhodnocení
5. Přechod na další otázku nebo finální obrazovku

## 7. Důležité provozní soubory

- `main.py`: vstupní bod aplikace
- `prepare_questions.py`: příprava dat pro hru
- `run_tests.py`: spouštění testů
- `ADMIN_GUIDE.md`: návod pro přípravu otázek
- `PRE_DEPLOYMENT_CHECKLIST.md`: kontrolní seznam před nasazením

## 8. Poznámka k historickým dokumentům

Historické etapové reporty byly odebrány, protože byly zastaralé a duplikovaly informace, které už jsou v aktuálních hlavních dokumentech (`README.md`, `ADMIN_GUIDE.md`, `SECURITY_FAQ.md`, `PROJECT_COMPLETE.md`).
