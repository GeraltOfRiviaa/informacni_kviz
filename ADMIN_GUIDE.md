# ADMIN GUIDE - Příprava Quiz Otázek

**Určeno pro:** Administrátora/tvůrce soutěže  
**Verze:** 1.0  
**Cíl:** Bezpečné vytvoření datových souborů pro quiz aplikaci

---

## Přehled Procesu

```
1. Příprava
   ├─ Sběr otázek (papír, dokument)
   └─ Sběr obrázků (disk)

2. Organizace
   ├─ Vytvoření adresářové struktury
   ├─ Přejmenování obrázků (anonymně)
   └─ Vytvoření JSON vstupního souboru

3. Transformace (AUTOMATICKÁ)
   ├─ prepare_questions.py
   ├─ Hashování odpovědí
   ├─ Randomizace image_ids
   └─ Vytvoření ZIP archívu

4. Čištění
   ├─ Smazání originálů
   └─ Ověření databáze
```

---

## Krok 1: Příprava Otázek

### 1.1 Sbírání Dat

**Upravit online dokument** (např. Google Docs) se sloupci:
```
| Kategorie | Odpověď | Obrázek | Obtížnost | Poznámka |
|-----------|---------|---------|-----------|----------|
| personality | Steve Jobs | steve_jobs.jpg | medium | Apple |
| logo | Google | google_logo.jpg | easy | Search |
| hardware | GPU | nvidia_gpu.jpg | hard | Graphics |
```

**Nebo fyzicky na papíře:**
```
Otázka 1: Kdo založil Apple?
Odpověď: Steve Jobs
Obrázek: Foto Steve Jobse
Obtížnost: medium

Otázka 2: Loga kterýc firem vidíte?
Odpověď: Google
Obrázek: Google logo
Obtížnost: easy

...
```

### 1.2 Sbírání Obrázků

**Kde vzít obrázky:**
- Google Images (s licencí)
- Wikipedia
- Vlastní fotografie
- Pixabay, Unsplash (free)

**Jaký formát:**
- PNG nebo JPG (nejčastější)
- Velikost: 800×600 px (bude se dělit na 4×4)
- Rozlišitelný obsah (ne příliš malý, ne příliš velký)

---

## Krok 2: Organizace Souborů

### 2.1 Adresářová Struktura

```
informacni_kviz/
├── original_data/                  ← ZDE PRACUJETE
│   ├── questions_input.json        ← Vstupní JSON s plaintext
│   └── images/                     ← Originální obrázky
│       ├── steve_jobs.jpg
│       ├── google_logo.jpg
│       └── nvidia_gpu.jpg
│
├── data/                           ← VÝSTUP prepare_questions.py
│   ├── questions.json              ← Bezpečné (s hashy)
│   └── config.json                 ← Nastavení
│
├── assets/
│   └── images_archive.zip          ← VÝSTUP (všechny obrázky)
│
└── prepare_questions.py            ← SPUSŤTE TOTO
```

### 2.2 Vytvoření original_data/ Adresáře

```powershell
# Ve Windows PowerShellu:
New-Item -ItemType Directory -Path "original_data\images" -Force
```

```bash
# V Linux/Mac:
mkdir -p original_data/images
```

### 2.3 Přejmenování Obrázků (Anonymně!)

❌ **ŠPATNĚ:**
```
steve_jobs.jpg         ← Zrada!
google_logo.jpg        ← Zrada!
nvidia_gpu.jpg         ← Zrada!
```

✅ **SPRÁVNĚ:**
```
image_001.jpg          ← Čistě anonymní
image_002.jpg
image_003.jpg
```

**Nebo ještě lépe - bez pořadí:**
```
img_001.jpg
img_042.jpg
img_123.jpg
```

**Protože script poté randomizuje image_ids, takže:**
- otázka q001 nemusí mít img_001
- otázka q001 může mít img_087
- Nikdo neví jaké je mapování

---

## Krok 3: Vytvoření questions_input.json

### 3.1 JSON Formát

Vytvořte soubor `original_data/questions_input.json`:

```json
{
  "questions": [
    {
      "answer": "Steve Jobs",
      "image": "image_001.jpg",
      "category": "personality",
      "difficulty": "medium",
      "description": "Apple founder - Jobs visibly in the photo"
    },
    {
      "answer": "Google",
      "image": "image_002.jpg",
      "category": "logo",
      "difficulty": "easy",
      "description": "Search engine logo"
    },
    {
      "answer": "GPU",
      "image": "image_003.jpg",
      "category": "hardware",
      "difficulty": "hard",
      "description": "Graphics Processing Unit - NVIDIA"
    },
    {
      "answer": "Linux",
      "image": "image_004.jpg",
      "category": "operating_system",
      "difficulty": "medium",
      "description": "Open-source OS, Linus Torvalds"
    }
  ]
}
```

### 3.2 Vysvětlení Polí

| Pole | Typ | Povinné | Popis |
|---|---|---|---|
| `answer` | string | ✅ | Správná odpověď (např. "Steve Jobs") |
| `image` | string | ✅ | Jméno obrázku v `original_data/images/` |
| `category` | string | ❌ | Kategorie (personality, logo, hardware, ...) |
| `difficulty` | string | ❌ | "easy", "medium", "hard" |
| `description` | string | ❌ | Popis pro admina (NEOBJEVÍ se v aplikaci) |

### 3.3 Pokyny k `answer` Poli

- ✅ Napište přirozené odpovědi: "Steve Jobs", "Google", "Python"
- ✅ Akceptujeme diakritiku: "Štěpán", "Václav"
- ✅ Akceptujeme velká/malá písmena: "GOOGLE", "Steve"
- ✅ Script to normalizuje automaticky

---

## Krok 4: Příprava Obrázků

### 4.1 Kvalita Obrázků

**Doporučené:**
```
- Rozměr: 800×600 px (nebo 1024×768)
- Formát: JPG nebo PNG
- Velikost souboru: 100-500 KB na obrázek
- Kontrast: Dostatečně čitelný
```

**Testovací příkaz - změna velikosti (Python PIL):**
```python
from PIL import Image

img = Image.open("image_001.jpg")
img = img.resize((800, 600))  # změníč na 800×600
img.save("image_001_resized.jpg", quality=85)
```

### 4.2 Bezpečnostní Tipy

- ❌ NEUKLÁDEJTE obrázky v **original_data/images/** s originálními názvy (`steve_jobs.jpg`)
  → Po spuštění prepare_questions.py se smaží!

- ✅ POUŽÍVEJTE anonymní názvy (`image_001.jpg`, `image_042.jpg`)
  → Script si bez obav vezme a randomizuje

- 💾 Udělej si **zálohu původních obrázků**
  - Např. `MyPhotos_backup/`
  - Protože prepare_questions.py je smažou po spuštění!

---

## Krok 5: Spuštění prepare_questions.py

### 5.1 Předpoklady

```bash
# Nainstalujte závislosti:
pip install pillow cryptography

# (Nebo upravte requirements.txt)
```

### 5.2 Spuštění Skriptu

```bash
# Cd do adresáře projektu
cd C:\Users\SAM\Documents\SSPU\Python\informacni_kviz

# Spusťte script
python prepare_questions.py
```

### 5.3 Expected Output

```
======================================================================
🔐 PŘÍPRAVA QUIZ DAT - BEZPEČNÁ TRANSFORMACE
======================================================================

1️⃣  Validace vstupů...
✅ Vstupní soubory OK

2️⃣  Transformace otázek...
📋 Načteno 4 otázek...
✅ q001: img_087 - stevejobs...
✅ q002: img_003 - google...
✅ q003: img_156 - gpu...
✅ q004: img_042 - linux...

3️⃣  Vytvoření archívu s obrázky...
📦 Vytváření ZIP archívu s obrázky...
  ✅ image_001.jpg → img_087.jpg
  ✅ image_002.jpg → img_003.jpg
  ✅ image_003.jpg → img_156.jpg
  ✅ image_004.jpg → img_042.jpg
✅ ZIP archiv vytvořen: assets/images_archive.zip

4️⃣  Uložení questions.json...
✅ Otázky uloženy: data/questions.json

5️⃣  Čištění originálů...
⚠️  POZOR: Chcete smazat originální obrázky z original_data/images/?
Zadejte 'ano' pro potvrzení: ano
🗑️  Všechny obrázky ze original_data/images smazány.

======================================================================
✅ PŘÍPRAVA KOMPLETNÍ!
======================================================================

Výstupy:
  ✅ data/questions.json
  ✅ assets/images_archive.zip
  ✅ Originální obrázky: smazány
```

### 5.4 Co Se Stalo?

**Bez tajných odpovědí:**

1. **questions.json** - Obsahuje POUZE:
   ```json
   {
     "id": "q001",
     "image_id": "img_087",
     "answer_hash": "a3f5b8c2d1e9f4a6...",
     "answer_salt": "x9k2m5n8p1q4r7s0...",
     "answer_length": 9
   }
   ```
   → Žádné "Steve Jobs"!

2. **images_archive.zip** - Obsahuje:
   ```
   img_087.jpg  (z image_001.jpg, který byl Steve Jobs)
   img_003.jpg  (z image_002.jpg, který byl Google)
   img_156.jpg  (z image_003.jpg, který byl GPU)
   img_042.jpg  (z image_004.jpg, který byl Linux)
   ```
   → Žádné indicie v názvech!

3. **Originální adresář** - Smazán
   ```
   original_data/images/  (prázdný)
   ```
   → Už se nemůžete vrátit k originálům (má to smysl!)

---

## Krok 6: Ověření Dat

### 6.1 Kontrolní seznam

- [ ] `data/questions.json` existuje a je čitelný
- [ ] `assets/images_archive.zip` existuje
- [ ] Počet otázek v JSON = počet obrázků v ZIP
- [ ] Žádné plaintext "Steve Jobs" v questions.json (ani v souborech!)
- [ ] image_ids jsou randomizované (ne img_001, img_002, ...)

### 6.2 Ověření JSON (Python)

```python
import json

with open("data/questions.json") as f:
    data = json.load(f)
    
for q in data["questions"]:
    print(f"{q['id']}: {q['image_id']} → {q['answer_hash'][:16]}...")
    # Ověř: není tam "Steve" ani "Google"!
```

### 6.3 Ověření ZIP (Python)

```python
import zipfile

with zipfile.ZipFile("assets/images_archive.zip") as zf:
    print("Soubory v ZIP:")
    for name in zf.namelist():
        print(f"  - {name}")  # img_087.jpg, img_003.jpg, ...
```

---

## Krok 7: Běhná Údržba

### 7.1 Přidání Nové Otázky

Postup:
1. Přidejte řádek do `original_data/questions_input.json`
2. Přidejte obrázek do `original_data/images/`
3. Spusťte znovu `prepare_questions.py`
4. Systém vše znovu zabezpečí a randomizuje

### 7.2 Změna Existující Otázky

```
❌ Upravování questions.json ručně = NEBEZPEČNÉ!
✅ Vždy: Přeformuluj questions_input.json + spusť prepare_questions.py
```

### 7.3 Zálohování

**Důležité zálohovat:**

```
ZÁLOHA A:
├── data/questions.json
└── assets/images_archive.zip

(Tyto jsou již zabezpečené, není v tom plaintext)

ZÁLOHA B (PRO ADMIN):
├── original_data/questions_input.json (papírová verze v sejfu!)
└── MyPhotos_backup/ (originální obrázky, kdyby bylo potřeba)

(Tuto uschovej MIMO pracovní adresář!)
```

---

## Bezpečnostní Checklista

- [ ] Žádné plaintext odpovědi ve slučích (jen v original_data/)
- [ ] Obrázky pojmenované anonymně (image_001, image_042, ...)
- [ ] prepare_questions.py spuštěn a úspěšně
- [ ] questions.json neobsahuje odpovědi (jen hashe)
- [ ] images_archive.zip neobsahuje jména odpovědí
- [ ] Originální obrázky smazány z original_data/images/
- [ ] Fyzická záloha questions_input.json v sejfu
- [ ] Backup obrázků uschovány mimo pracovní adesář

---

## Časté Chyby

| Chyba | Příčina | Řešení |
|---|---|---|
| `FileNotFoundError` | Obrázek nenalezen | Zkontroluj jméno v JSON |
| `JSONDecodeError` | Chybný JSON | Ověř JSON syntax (https://jsonlint.com/) |
| `PermissionError` | ZIP je otevřený | Zavři ZIP archiv |
| Duplikátní questions | Spuštěno 2× | Smaž `data/questions.json` a znovu |

---

## Příkladní Komplexní Otázka

```json
{
  "answer": "Alan Turing",
  "image": "image_050.jpg",
  "category": "personality",
  "difficulty": "hard",
  "description": "Father of computer science and AI, WWII codebreaker at Blehchley Park"
}
```

Po spuštění prepare_questions.py:
```json
{
  "id": "q050",
  "image_id": "img_234",
  "answer_hash": "b7c3e8f1a2d4c9b5...",
  "answer_salt": "p2w5x8z1m4r7s0t3...",
  "answer_length": 10,
  "category": "personality",
  "difficulty": "hard"
}
```

✅ Žádné "Alan Turing"!
✅ Žádný odkaz na image_050!
✅ Bezpečně!

---

## Support

Pokud máte otázky:
- Podívejte se na `docs/design.md` (Bezpečnost - kapitola 7)
- Spusťte `python prepare_questions.py --help` (pokud je implementován)
- Zkontrolujte `original_data/questions_input.json` syntax

---

**Hotovo?** Nyní můžete spustit aplikaci! 🚀

```bash
python main.py
```
