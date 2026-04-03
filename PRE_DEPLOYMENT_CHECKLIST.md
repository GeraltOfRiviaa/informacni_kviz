# Kontrolní Seznam Před Nasazením

Kontrolní seznam pro přípravu aplikace před reálnou soutěží.

## 1. Testy a start aplikace

- [ ] `python main.py` startuje bez běhové chyby
- [ ] je možné otevřít admin režim i herní režim

## 2. Data a obrázky

- [ ] `data/questions.json` je validní JSON
- [ ] každá otázka má `id`, `image_id`, `answer_hash`, `answer_salt`, `answer_length`
- [ ] v `data/questions.json` není plaintext pole `answer`
- [ ] pro každé `image_id` existuje soubor v `assets/images/`
- [ ] v `assets/images/` nejsou placeholdery pro produkci

## 3. Admin bezpečnost

- [ ] výchozí heslo bylo změněno
- [ ] uzamčení po neúspěšných pokusech funguje
- [ ] administrační panel je dostupný jen organizátorovi

## 4. Herní UX

- [ ] timer je viditelný a odčítá korektně
- [ ] kliknutí na buňku odkrývá část obrázku
- [ ] nápověda písmen funguje
- [ ] penalizace se promítá do skóre
- [ ] odeslání odpovědi zobrazí výsledek kola

## 5. Operační příprava

- [ ] připravena záloha složek `data/` a `assets/images/`
- [ ] stroj je v režimu bez rušivých aplikací
- [ ] otestováno na cílovém monitoru/projektoru
- [ ] obsluha zná postup pro restart kola

## 6. Doporučené příkazy

```bash
python prepare_questions.py
python main.py
py build_exe.py
```
