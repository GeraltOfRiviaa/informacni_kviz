# Uživatelský průvodce

Tento dokument je krátký provozní návod pro organizátora soutěže.

## 1. Spuštění

```bash
python main.py
```

Po spuštění zvol režim:

- admin
- hra

## 2. Herní režim

- Vyber tým a obtížnost.
- V kole odhaluješ části obrázku (4x4).
- Zadáš odpověď do vstupu a odešleš.
- Body se odečítají za odhalená pole, nápovědy a špatné odpovědi.

## 3. Admin režim

- Kontrola a správa otázek.
- Práce s obrázky.
- Úpravy dat otázek pro běh aplikace.

## 4. Datové soubory

- Runtime otázky: `data/questions.json`
- Vstupní otázky: `original_data/questions_input.json`
- Runtime obrázky: `assets/images/`
- Vstupní obrázky: `original_data/images/`

## 5. Příprava runtime dat

```bash
python prepare_questions.py
```

Skript připraví hashované otázky a runtime obrázky.

## 6. Build distribuce

Doporučený build:

```bash
py build_exe.py
```

Jeden `.exe` build:

```bash
py build_exe.py --onefile
```

Výstupní soubory jsou ve složce `dist/`.

## 7. Nejčastější problémy

- Chybějící obrázek: zkontroluj cestu a formát (`jpg`, `jpeg`, `png`, `gif`, `webp`).
- Žádné otázky: ověř obsah `data/questions.json`.
- Nefunkční build: doinstaluj závislosti přes `pip install -r requirements.txt`.
