# Stav Admin Systému

## Shrnutí

Admin část je implementovaná a integrovaná do hlavní aplikace. Podporuje:

- autentizaci správce
- CRUD operace nad otázkami
- upload obrázků do `assets/images/`
- filtraci a vyhledávání
- správu dat pro následné spuštění herního režimu

## Hlavní komponenty

- `services/admin_auth.py` - hash hesla, lockout, verifikace
- `services/admin_question_manager.py` - správa `data/questions.json`
- `services/image_upload_service.py` - validace a uložení obrázků
- `ui/admin_startup_screen.py` - volba režimu
- `ui/admin_login_screen.py` - přihlašovací dialog
- `ui/admin_panel.py` a `ui/admin_question_panel.py` - správa otázek

## Bezpečnost

- odpovědi jsou hashované (`answer_hash`, `answer_salt`)
- validace vstupu a struktury otázek
- lockout po neúspěšných přihlášeních
- kontrola typu obrázků pomocí magic bytes

## Poznámky k provozu

- výchozí heslo je určeno jen pro vývoj; před soutěží ho změňte
- aplikace umí běžet i s placeholder obrázky, ale pro reálné použití doplňte skutečné soubory
- přípravu otázek a anonymní mapování obrázků dělá `prepare_questions.py`

## Doporučené ověření

```bash
python main.py
py build_exe.py
```
