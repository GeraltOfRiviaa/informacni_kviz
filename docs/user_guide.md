# Uživatelský Průvodce - Informační Kvíz

**Verze:** 1.0  
**Poslední aktualizace:** Duben 2026  
**Cíl:** Průvodce pro operátory a soutěžící při používání aplikace Informační Kvíz

---

## Obsah

1. [Přehled Aplikace](#přehled-aplikace)
2. [Požadavky a Instalace](#požadavky-a-instalace)
3. [Spuštění Aplikace](#spuštění-aplikace)
4. [Hlavní obrazovky](#hlavní-obrazovky)
5. [Hra - Detailní Průvodce](#hra---detailní-průvodce)
6. [Správa Otázek](#správa-otázek)
7. [Řešení Problémů](#řešení-problémů)
8. [Bezpečnost](#bezpečnost)
9. [FAQ](#faq)

---

## Přehled Aplikace

**Informační Kvíz** je edukativní soutěž pro 3-členné týmy základních škol.

### Základní Princip
- Každé kolo obsahuje **jeden obrázek** skrytý za mřížkou **4×4 políček** (16 políček celkem)
- Soutěžící postupně **odkrývají políčka** (za body)
- Dostávají **písmenové nápovědy** (also za body)
- Cíl: Uhodnout, co je na obrázku (jméno, název, pojmenování)

### Scoring
```
1. políčko:       0 bodů  (zdarma)
2. politčko:     -1 bod
3. politčko:     -2 body
...atd (lineární pokles)
Chybná odpověď:  -20 bodů
Nápověda (písmeno): -1 až -N bodů
```

**Výsledek:** Počet bodů = max(0, počáteční_body - odečet_za_políčka - odečet_za_nápovědy)

---

## Požadavky a Instalace

### Systémové Požadavky
- **Windows 10/11** nebo **Linux/macOS**
- **Python 3.8+** (pokud spouštíte ze zdrojových kódů)
- Minimum **2 GB RAM**
- Displej **1920×1080** nebo větší (doporučeno pro promítání)

### Instalace ze Zdrojových Kódů

```bash
# 1. Klonujte projekt
git clone https://github.com/GeraltOfRiviaa/informacni_kviz.git
cd informacni_kviz

# 2. Vytvořte virtuální prostředí
python -m venv .venv

# 3. Aktivujte prostředí
# Windows:
.\.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 4. Instalujte závislosti
pip install -r requirements.txt

# 5. Spusťte aplikaci
python main.py
```

### Instalace Standalone Aplikace (EXE)
1. Stáhněte `informacni_kviz_v1.0.exe` z release stránky
2. Spusťte instalátor
3. Vytvoří se zástupce na ploše
4. Aplikace je připravena k použití

---

## Spuštění Aplikace

### Příkazová Řádka

```bash
# Normální spuštění
python main.py

# Debug režim (verbose logging)
python main.py --debug

# Režim pro testování (bez ukládání výsledků)
python main.py --test
```

### GUI Spuštění
1. Dvakliknutí na `informacni_kviz.exe` (nebo Python soubor `main.py`)
2. Aplikace se spustí s **úvodní obrazovkou**

---

## Hlavní Obrazovky

### 1. Úvodní Obrazovka
```
╔════════════════════════════════════════╗
║     INFORMAČNÍ KVÍZ - SOUTĚŽ          ║
║                                        ║
║  • Počet týmů: [_____]                 ║
║  • Počet kol: [_____]                 ║
║                                        ║
║      [Spustit Soutěž]                 ║
║      [Nastavení]                      ║
║      [Konec]                          ║
╚════════════════════════════════════════╝
```

**Akce:**
- Zadejte počet soutěžících týmů (2-4)
- Nastavte počet kol (1-10)
- **Spustit Soutěž** → přechod na obrazovku týmů

### 2. Registrace Týmů
```
╔════════════════════════════════════════╗
║      REGISTRACE TÝMŮ                  ║
║                                        ║
║  Tým 1: [__________________]           ║
║  Tým 2: [__________________]           ║
║  Tým 3: [__________________]           ║
║                                        ║
║      [Pokračovat]   [Zpět]            ║
╚════════════════════════════════════════╝
```

**Akce:**
- Zadejte jméno každého týmu
- **Pokračovat** → spuštění prvního kola

### 3. Herní Obrazovka (Hlavní)
```
┌──────────────────────────────────────────┐
│  ┌──────────┐                            │
│  │ Čas: 9:32│    Tým: SKAPÁNI HRÁČI    │
│  │ Skóre: 87│    Pokus: 1/2             │
│  └──────────┘                            │
├──────────┬──────────────────────────────┤
│ Mřížka   │   Obrázek (částečně)        │
│ [_][_]   │   [███████ ░░░░░░░░░░]      │
│ [_][▓]   │   [███ ░░░░░░░░░░░░░░░]     │
│ [▓][_]   │   (Pixelované / Rozmazané)  │
│ [_][_]   │                             │
├──────────┴──────────────────────────────┤
│  Nápověda: S _ _ V E   _ O B _         │
│                                        │
│  Moje odpověď: [_____________________] │
│                                        │
│  [ Odhalitpísmeno ] [ Odeslat ]        │
└──────────────────────────────────────────┘
```

**Ovládání:**
- Klikněte na políčka v mřížce → odkryjte část obrázku
- **Odhalitpísmeno** → ukazuje jedno náhodné písmeno za -1 bod
- Zadejte odpověď do pole
- **Odeslat** → ověření odpovědi

### 4. Výsledek Kola
```
╔════════════════════════════════════════╗
║        VÝSLEDEK KOLA                  ║
║                                        ║
║  Správná odpověď: STEVE JOBS          ║
║  Váš pokus: Steve Jobs ✓               ║
║                                        ║
║  Odkrytých políček: 4     -4 bodů      ║
║  Použito nápověd: 2      -2 body       ║
║                                        ║
║  CELKEM BODŮ: +81 bodů                 ║
║                                        ║
║         [Další Kolo]  [Skončit]        ║
╚════════════════════════════════════════╝
```

### 5. Konečné Pořadí
```
╔════════════════════════════════════════╗
║      FINÁLNÍ POŘADÍ SOUTĚŽE           ║
║                                        ║
║  1. 🥇 SKAPÁNI HRÁČI        456 bodů   ║
║  2. 🥈 INFORMATICI           423 bodů   ║
║  3. 🥉 HACKEŘI               298 bodů   ║
║                                        ║
║  Vítězný tým: SKAPÁNI HRÁČI!           ║
║                                        ║
║         [Nová Soutěž]  [Konec]        ║
╚════════════════════════════════════════╝
```

---

## Hra - Detailní Průvodce

### Krok 1: Příprava Kola
1. Operátor vybere otázku (automaticky nebo ručně)
2. Aplikace načte obrázek a skryje ho za mřížkou 4×4
3. Soutěžící se rozhodnou, kdo bude hrát

### Krok 2: Odkrývání Políček
```
Každé odkryté políčko stojí body:
┌─────────────────────────┐
│ Pořadí | Body          │
├─────────────────────────┤
│    1   │  0 bodů       │ ← ZDARMA!
│    2   │ -1 bod        │
│    3   │ -2 body       │
│    4   │ -3 body       │
│   ...  │ ...           │
│   16   │ -15 bodů      │
└─────────────────────────┘
```

### Krok 3: Nápovědy
```
Možnost 1: Odhalitpásmeno (automatické)
  → Vyberou se náhodná písmena
  → Stojí -1 bod za jedno písmeno
  
Možnost 2: Práce s obrázkem
  → Více políček = lépe vidíte obrázek
  → Ale stojí to více bodů
```

### Krok 4: Odpověď
1. Soutěžící napíší odpověď do pole
2. Aplikace kontroluje:
   - **Bez rozdílu big/malých písmen** (Steve Jobs = steve jobs = STEVE JOBS)
   - **Bez diakritiky** (e = ě, s = š, atd.)
   - **Bez nadbytečných mezer**
3. **Správně** → Zobrazení výsledku a bodů
4. **Špatně** → -20 bodů, další pokus

---

## Správa Otázek

### Formát Datového Souboru

Otázky jsou uloženy v `data/questions.json`:

```json
[
  {
    "id": "q001",
    "image": "steve_jobs",
    "answer": "Steve Jobs",
    "answer_hash": "7d1a8f9b2c...",  // SHA256 hash
    "hints": [
      "Steve",
      "Jobs",
      "Apple",
      "Founder"
    ],
    "difficulty": "easy",
    "category": "personalities"
  },
  ...
]
```

### Přidání Nové Otázky

1. **Příprava obrázku:**
   ```bash
   # Umístěte obrázek do assets/images/
   assets/images/my_image.jpg
   ```

2. **Generování hashe odpovědi:**
   ```bash
   python prepare_questions.py --add-hash
   ```

3. **Přidání do questions.json:**
   ```json
   {
     "id": "q999",
     "image": "my_image",
     "answer": "My Answer",
     "answer_hash": "[vygenerete skriptem]",
     "hints": ["My", "Answer", "..."]
   }
   ```

### Bezpečnost Otázek
- **NIKDY** neukládejte odpovědi v plaintext!
- Odpovědi jsou uloženy jako **SHA256 hashe**
- Ověření odpovědi probíhá interně (kontrolou hashe)
- Viz [Bezpečnost](#bezpečnost) níže

---

## Řešení Problémů

### Problém: Aplikace se nespustí

**Řešení:**
```bash
# Zkontrolujte Python verzi
python --version  # mělo by být 3.8+

# Zkontrolujte instalaci závislostí
pip install -r requirements.txt

# Spusťte s debug režimem
python main.py --debug
```

### Problém: Obrázky se nenačítají

**Řešení:**
1. Zkontrolujte cestu `assets/images/`
2. Zkontrolujte, že soubor opravdu existuje
3. Zkontrolujte příponu (`.jpg`, `.png`)
4. V debug režimu vidíte přesnou chybu

```bash
python main.py --debug
# V logu vidíte: "ERROR: Image 'xyz' not found"
```

### Problém: Odpovědi nejsou rozpoznány

**Běžné příčiny:**
- Pravopis (zkontrolujte questions.json)
- Diakritika (aplikace ji odstraňuje - je to OK)
- Mezery (aplikace je odstraňuje - je to OK)

**Řešení:**
```bash
# Resetujte hashe
python prepare_questions.py --regenerate-hashes

# Zkontrolujte odpověď v aplikaci (debug režim)
```

### Problém: GUI se zobrazuje špatně

**Řešení:**
1. Zkontrolujte rozlišení displeje (1920×1080 minimum)
2. Zkontrolujte instalaci tkinter:
   ```bash
   pip install tk
   ```
3. Zkontrolujte, že nejste v malém okně - zkuste fullscreen (F11)

### Problém: Časovač nefunguje

**Řešení:**
```bash
# Kontrola logu
python main.py --debug

# Ifax problém trvá, zkontrolujte:
# 1. Není-li aplikace v pauze
# 2. Není-li vypršel čas už před spuštěním
```

---

## Bezpečnost

### Ochrana Odpovědí

Aplikace používá **SHA256 hashing** pro kontrolu odpovědí:

```python
# Odpověď se normalizuje:
"Steve JÓBS" → "steve jobs"

# Pak se ověří hashem:
hash("steve jobs") == "7d1a8f9b2c..." ✓
```

**Výhody:**
- Operátor nevidí správné odpovědi v datech
- Není možné jednoduše „hacknout" aplikaci otevřením souboru
- Odpovědi jsou chráněny

### Zákaz Debug Modu
- Debug režim (`--debug`) je dostupný pouze pro vývoj
- Pro soutěž se používá normální režim
- Bez debug modu nejsou viditelné odpovědi

### Zálohování Výsledků
- Výsledky se automaticky ukládají do `data/results/`
- Každá soutěž má svůj soubor s časovým razítkem
- Doporučujeme řádné zálohování

---

## FAQ

### Otázka: Kolik týmů může hrát?
**Odpověď:** 2-4 týmy současně. Každý tým hraje postupně.

### Otázka: Jak dlouho trvá jedno kolo?
**Odpověď:** Standardně 10 minut (nastavitelné v config.json).

### Otázka: Lze měnit otázky během soutěže?
**Odpověď:** Ano, v administračním panelu (zatím ruční přidání do JSON).

### Otázka: Co když se aplikace zhroutí?
**Odpověď:** Výsledky jsou uloženy v `data/results/` - data nejsou ztracena.

### Otázka: Jak překontrolovat skóre?
**Odpověď:** V souborech v `data/results/` jsou uloženy všechny detaily (odkrytá políčka, nápovědy, body).

### Otázka: Lze spustit offline?
**Odpověď:** Ano! Aplikace není závislá na internetu. Všechna data jsou lokální.

### Otázka: Jaké jsou systémové nároky?
**Odpověď:** Minimum 2 GB RAM, Python 3.8+, doporučeno moderní CPU. Běží na jakémkoli počítači s Pythonem.

### Otázka: Jak vytvořit standalone EXE?
**Odpověď:** Viz [Nasazení - PyInstaller](#nasazeni).

---

## Nasazení

### Vytvoření Standalone Aplikace

```bash
# 1. Nainstalujte PyInstaller
pip install pyinstaller

# 2. Spusťte build skript
python build_exe.py

# 3. Výsledný EXE je v dist/informacni_kviz/
#    Zkopírujte na cílový počítač a spusťte
```

Viz `build_exe.py` pro detaily.

---

## Kontakt a Podpora

**Autor:** Školský tým  
**Email:** support@informacni-kviz.cz  
**Repozitář:** https://github.com/GeraltOfRiviaa/informacni_kviz

**Zpracováno:** Duben 2026
