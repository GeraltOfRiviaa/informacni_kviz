# Interaktivní Informační Kvíz

Desktop aplikace v Pythonu/Tkinter pro školní týmovou soutěž. Hra funguje na principu postupného odhalování obrázku v mřížce 4x4 a odhadu správné odpovědi při co nejvyšším skóre.

## Aktuální stav

- Stav projektu: funkční prototyp s admin režimem, herním kolem, timerem a scoringem
- Uložení obrázků: normální soubory v `assets/images/` (ZIP už se nepoužívá)
- Ochrana odpovědí: `SHA256(answer_normalized + salt)`
- Testy: jádro, admin služby, GUI komponenty

## Hlavni vlastnosti

- 4x4 odhalovací mřížka s penalizací po jednotlivých tazích
- Nápověda přes odhalování písmen
- Časový limit na kolo
- Admin panel pro správu otázek
- Upload obrázků s validací formátu a velikosti
- Lokální JSON data bez závislosti na internetu

## Struktura dat

`data/questions.json` obsahuje pouze bezpečná pole:

```json
{
  "id": "q001",
  "image_id": "img_1234",
  "answer_hash": "...",
  "answer_salt": "...",
  "answer_length": 9,
  "difficulty": "easy",
  "category": "logo"
}
```

Runtime obrázek je hledán jako soubor:

- `assets/images/img_1234.jpg`
- nebo `assets/images/img_1234.png`
- atd. (`jpeg`, `webp`, `gif`)

## Rychlý start

1. Instalace závislostí

```bash
pip install -r requirements.txt
```

2. Spuštění aplikace

```bash
python main.py
```

3. Rychlý smoke test GUI

```bash
python test_gui_init.py
```

## Příprava otázek a obrázků

Použij admin skript:

```bash
python prepare_questions.py
```

Skript:

1. načte `original_data/questions_input.json`
2. zahashuje odpovědi
3. vygeneruje anonymní `image_id`
4. nakopíruje obrázky do `assets/images/` pod anonymními názvy
5. uloží `data/questions.json`

Pokud chybí zdrojový obrázek, skript vytvoří placeholder, aby hra zůstala spustitelná.

Detailní návod: `ADMIN_GUIDE.md`

## Bezpečnost

- Odpovědi nejsou nikde ukládané v plaintextu
- Kontrola odpovědi probíhá hash porovnáním po normalizaci vstupu
- `image_id` je anonymní a neobsahuje název odpovědi
- Admin funkce mají autentizaci a lockout po opakovaných neúspěšných pokusech

Detailní FAQ: `SECURITY_FAQ.md`

## Testování

Doporučené minimální ověření:

```bash
pytest tests/test_image_handler.py tests/test_round_manager.py tests/test_config_utils.py -q
```

Kompletní sada:

```bash
pytest tests -q
```

## Důležité soubory

- `main.py` - vstupní bod aplikace
- `gui.py` - orchestrace obrazovek a toku hry
- `ui/round_screen.py` - herní obrazovka
- `services/image_handler.py` - načítání a maskování obrázků
- `prepare_questions.py` - příprava produkčních dat
- `services/admin_question_manager.py` - CRUD otázek

## Poznámka k obrázkům

Repozitář momentálně může být bez reálných obrázků (kvůli velikosti a právům). Aplikace proto umí zobrazit placeholder a zůstane funkční. Pro reálnou soutěž doplňte skutečné obrázky do `original_data/images/` a spusťte `prepare_questions.py`.
