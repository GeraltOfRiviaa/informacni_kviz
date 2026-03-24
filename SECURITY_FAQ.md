# Bezpečnost - FAQ (Často Kladené Otázky)

**Zdroj:** Odpovědi na klíčové bezpečnostní otázky  
**Určeno pro:** Vývojáře, administrátory, učitele

---

## ❓ Otázka 1: Jak Se Poznají Mapování Otázka → Obrázek?

### Problém
"Když vytvořím otázku s odpovědí 'Steve Jobs' a uložím ji jako `q001`, a obrázek jako `img_001`, tak přece někoho napadne: otázka 1 → obrázek 1 → musí to být Steve Jobs?"

### Řešení: RANDOMIZACE Image_ID

Script `prepare_questions.py` si **není sekvenciální** mapování!

**Příklad:**
```json
// questions.json (vyprodukováno prepare_questions.py)
q001 → image_id: "img_087"  (žádná logika!)
q002 → image_id: "img_003"  (náhodné)
q003 → image_id: "img_156"  (nepředvídatelné)
q004 → image_id: "img_042"  (bez vzoru)
```

### Jak Funguje Randomizace?

```python
# V prepare_questions.py:
def generate_random_image_ids(count: int) -> List[str]:
    """Generuje NÁHODNÉ image_ids v rozsahu 1-10000"""
    image_ids = [f"img_{secrets.randbelow(10000):04d}" for _ in range(count)]
    return image_ids

# Výsledky:
# ["img_0087", "img_0003", "img_0156", "img_0042", ...]
# Zcela nepředvídatelné!
```

### Bezpečnostní Složitost

Pokud by někdo chtěl deducovat mapování:

```
Zná: q001 → img_087
Chce: Zjistim jaká je to odpověď

Možnosti:
❌ Z jména img_087? → Není nápověda (anonymní)
❌ Z pořadí? → Není sekvence (náhodné)
❌ Z hash? → SHA256 je jednosměrný
❌ Z ZIP archívu? → Soubory jsou bez názvu

Závěr: NEMOŽNÉ bez znalosti answer_hash!
```

---

## ❓ Otázka 2: Jak Zabránit Uživateli V Otevření Obrázků?

### Problém
"Když máte obrázky v `assets/images_archive.zip`, uživatel je prostě otevře přes Windows Explorer, nebo rozbalí ZIP a vidí 'img_087.jpg' - neřekne si nic, ale teoreticky by je mohl vidět."

### Řešení: Více Vrstev Ochrany

#### Vrstva 1: ZIP Archiv
```
assets/images_archive.zip
```
- Obrázky nejsou jednotlivě v adresáři
- Jsou zabalené v ZIP
- Není to zásadní ochrana, ale je to prvníbariera

#### Vrstva 2: Runtime Dekomprese
```python
# V aplikaci (image_handler.py):
import zipfile

with zipfile.ZipFile("assets/images_archive.zip") as zf:
    image_bytes = zf.read("img_087.jpg")  # Čte z paměti
    # Obrázek se NIKDY neukládá na disk během hry!
```

- Obrázek se načte do paměti
- Není fyzicky na disku během hry
- Uživatel nemůže vidět chod dekomprese

#### Vrstva 3: Anonymní Jména
```
Obsah ZIP archivu:
├── img_087.jpg  ← NIKDO neví co to je
├── img_003.jpg
├── img_156.jpg
└── img_042.jpg
```

- Jméno `img_087.jpg` rovná nic
- I kdyby uživatel ZIP otevřel, viděl by jen `img_087.jpg`
- Bez kontextu nevěd co to znamená

#### Vrstva 4: Offline Admin Data
```
original_data/questions_input.json
  ├── answer: "Steve Jobs"     ← OFFLINE, ne v aplikaci!
  └── image: "image_001.jpg"   ← OFFLINE, smazáno po prepare!
```

- Mapování "image_001 = Steve Jobs" je jen v offline scriptu
- Po spuštění `prepare_questions.py` se originál smažou
- V aplikaci to mapování **neexistuje**!

### Best Practice: Šifrování (Pokročilé)

Pokud chcete **ultra-bezpečnost**, můžete ZIP zašifrovat:

```python
# prepare_questions.py - rozšíření:
import pyminizip

pyminizip.compress_multiple(
    "assets/images_archive.zip",
    "assets/images_archive_encrypted.zip",
    "super_tajne_heslo",
    compression_type=8
)
```

Pak by byl ZIP teoreticky zašifrován (ale ve stejné aplikaci).

**Poznámka:** Pro školský projekt to není nutné, protože:
- Obrázky nejsou tajné (jsou vidět v hře)
- Tajné je jenoMAPOVÁNÍ (budou obejmovat bez něj)
- Mapování je v paměti aplikace (ne v ZIP)

---

## ❓ Otázka 3: Kde Budou Obrázky Uloženy a Jak Zajistit Ochranu?

### Adresářová Struktura

```
informacni_kviz/
│
├── original_data/                    (PRACOVNÍ ADRESÁŘ)
│   ├── questions_input.json          (se plaintext odpověďmi)
│   └── images/
│       ├── image_001.jpg
│       ├── image_002.jpg
│       └── ...✅Smazáno po prepare!
│
├── data/                             (VÝSTUPY - bezpečné)
│   ├── questions.json                (bez plaintext)
│   ├── config.json
│   └── answers_hash.json
│
├── assets/                           (VÝSTUPY - bezpečné)
│   └── images_archive.zip            (všechny obrázky anonymně)
│
└── prepare_questions.py              (spuštěno jednou offline!)
```

### Fáze 1: Příprava (Admin, OFFLINE)

```
original_data/
├── questions_input.json
└── images/
    ├── image_001.jpg (Steve Jobs)
    ├── image_002.jpg (Google)
    └── image_003.jpg (GPU)
```

**Co se stane:**
1. Admin přidá otázky do `questions_input.json`
2. Admin přidá obrázky do `images/`
3. Admin spustí `python prepare_questions.py`

### Fáze 2: Transformace (Script)

Script provede:
1. Přečte `questions_input.json`
2. Hashuje odpovědi
3. **Randomizuje image_ids:**
   - image_001.jpg → img_087.jpg
   - image_002.jpg → img_003.jpg
   - image_003.jpg → img_156.jpg
4. Vytvoří ZIP s randomizovanými názvynimi
5. **Smažeoriginální obrázky!**

```
original_data/images/  ← SMAZÁNO!
```

### Fáze 3: Runtime (Aplikace)

```python
# game.py:
from zipfile import ZipFile

# Načti otázku
question = QuestionLoader.get("q001")
# → {"id": "q001", "image_id": "img_087", "answer_hash": "...", ...}

# Načti obrázek z ZIP (do paměti!)
with ZipFile("assets/images_archive.zip") as zf:
    image_bytes = zf.read("img_087.jpg")
    image = Image.open(BytesIO(image_bytes))

# Zobraz hráči
display_image(image)
```

### Ochrana Vrstvy Po Vrstvě

| Vrstva | Co Je Chráněné | Jak | Status |
|--------|---|---|---|
| **1. Soubory na Disku** | Mapování otázka→obrázek | Originály smazány | ✅ |
| **2. ZIP Archiv** | Fyzický přístup | Anonymní jména (img_087) | ✅ |
| **3. Paměť Aplikace** | Plaintext odpovědi | Jen hashe | ✅ |
| **4. HTTP/Transfer** | Pokud by se posílalo online | Šifrování SSL | ⚠️ *(pro budoucnost)* |
| **5. Executable (PyInstaller)** | Zdrojový kód | Obfuskace .pyc | ⚠️ *(pro budoucnost)* |

---

## 📌 Shrnutí: Jak Je To Bezpečné?

### Scénář 1: Uživatel Se Podívá do Disk

```
Pokus: Otevřít assets/images_archive.zip
Zjistí: img_087.jpg, img_003.jpg, img_156.jpg
Závěr: "Jsou to obrázky, ale neví kterého je co"
Bezpečnost: ✅ PASS
```

### Scénář 2: Uživatel Se Podívá do Paměti Aplikace

```
Pokus: Debugovat aplikaci, číst paměť
Zjistí: image_id="img_087", answer_hash="a3f5b8c2..."
Pokus: Dekódovat hash
Závěr: "SHA256 je jednosměrný, nemohu"
Bezpečnost: ✅ PASS
```

### Scénář 3: Uživatel Vidí Pořadí Otázek

```
Pokus: "Otázka 1 je img_087, musí být něco zvláštního"
Zjistí: img_087 nemá smysl (není sekvence)
Pokus: Koukat se na další otázky
Zjistí: q001→img_087, q002→img_003, q003→img_156
Závěr: "Žádný vzor, je to náhodné"
Bezpečnost: ✅ PASS
```

### Scénář 4: Uživatel/Hacker Má Python Znalost

```
Pokus: Spustit prepare_questions.py
Probléma: `original_data/questions_input.json` již neexistuje!
         (admin ho střežed v sejfu)
Závěr: "Bez vstupního souboru nemohu znovu generovat"
Bezpečnost: ✅ PASS (pokud admin správě chuje datos)
```

---

## 🔑 Klíčová Pravidla Pro Admina

1. **Fyzická záloha:**
   ```
   📄 original_data/questions_input.json
      → Vytiskni papír + sejf (nebo zašifrovaný USB)
   ```

2. **Nespouštěj prepare_questions.py během soutěže!**
   ```
   Řekni si všechny otázky a obrázky P1EDY.
   Pak jednou spusť prepare_questions.py a hlídej aplikaci.
   ```

3. **Nesmazuj ZIP!**
   ```
   ✅ Nechej: assets/images_archive.zip
   ❌ Nesmažuj: original_data/questions_input.json
     (máš ji v sejfu, nebo se vůbec nesmazuje)
   ```

4. **Hlídej přístup k aplikaci:**
   ```
   Během soutěže: Jen uživatelé hrají, nikdo se nepodívá do filesystému.
   ```

---

## 🛡️ Finální Bezpečnostní Checklist

- [ ] `original_data/questions_input.json` je v sejfu (fyzicky nebo šifrovaně)
- [ ] Originální obrázky jsou v zálohе mimo pracovní složku
- [ ] `prepare_questions.py` spuštěn jen jednou (nebo není přístupný)
- [ ] `data/questions.json` obsahuje jen hashe (bez odpovědí)
- [ ] `assets/images_archive.zip` existuje a je neporušený
- [ ] Originální obrázky ze `original_data/images/` smazány
- [ ] Image_ids jsou randomizované (ne img_001, img_002, ...)
- [ ] Aplikace počítá od ZIP do paměti (ne extrahuje na disk)
- [ ] Jen admin má přístup k prepare_questions.py
- [ ] Během soutěže mají přístup jen soutěžící k aplikaci

---

## Příklady z Praxe

### Příklad 1: Admin Chce Přidat Novou Otázku

```
SPRÁVNĚ:
1. Vezmi questions_input.json ze sejfu
2. Přidej řádek s novou otázkou
3. Vlož obrázek do original_data/images/
4. Spusť python prepare_questions.py
5. Otestuj aplikaci
6. Ulož questions_input.json zpět do sejfu
7. Smaž originální obrázky

ŠPATNĚ:
❌ Ručně edituj data/questions.json
❌ Kopíruj obrázky přímo do assets/
❌ Nespouštíš prepare_questions.py
```

### Příklad 2: Bezpečnostní Audit

```
KONTROLA:
1. Otevřu data/questions.json → vidím jen hashe ✅
2. Otevřu assets/images_archive.zip → vidím img_087, img_003, ... ✅
3. Měřím mapování q001→img_087 → žádný vzor ✅
4. Zkusím spustit prepare_questions.py → chybí questions_input.json ✅
   (admin ji má v sejfu)

VÝSLEDEK: Bezpečné! ✅
```

---

## Co když něco Selže?

| Problém | Příčina | Řešení |
|---------|---------|--------|
| Uživatel vidí plaintext odpověď | Admin špatně spustil script | Znovu: `python prepare_questions.py` |
| Obrázky jsou na disku jednotlivě | ZIP nebyl vytvořen | Zkontroluj `assets/images_archive.zip` |
| Image_ids jsou sekvenciální | Randomizace nefunguje | Update prepare_questions.py |
| Aplikace nemůže načíst obrázky | ZIP neexistuje | Spusť `prepare_questions.py` znovu |

---

**Máte další otázky?** Podívejte se na [ADMIN_GUIDE.md](ADMIN_GUIDE.md) nebo [docs/design.md](docs/design.md).
