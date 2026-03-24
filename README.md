# 🎯 Interaktivní Znalostní Soutěž - Informační Kvíz

**Projekt pro:** Tříčlenné týmy žáků základních škol  
**Jazyk:** Python 3.8+  
**Status:** 🟡 **Ve Vývoji (Fáze 1 - Design hotov)**  
**Verze:** 0.1.0

---

## 📋 Přehled Projektu

Interaktivní aplikace pro **znalostní soutěž** zaměřenou na **informační technologie**. Soutěžící skupiny postupně odkrývají obrázek skrytý za **mřížkou 4×4 políček**, aby uhodli, co je na obrázku (jméno osobnosti, název firmy, technologie, zařízení, apod.).

### Princip Hry

```
┌─────────────────────────────────┐
│  Obrázek (4×4 Mřížka)           │     Zbývající čas: 8:45
│  ┌──┬──┬──┬──┐                  │
│  │🔒│🔒│🔒│🔒│      Skóre: 95   │
│  ├──┼──┼──┼──┤                  │
│  │🔒│✓ │✓ │🔒│  Nápověda:       │  
│  ├──┼──┼──┼──┤      S _ _ _ _  │
│  │✓ │✓ │🔒│🔒│      J _ _ _    │
│  ├──┼──┼──┼──┤                  │
│  │🔒│🔒│🔒│✓ │  Odpověď:        │
│  └──┴──┴──┴──┘  ┌──────────────┐│
│                 │Steve Jobs    ││
│                 │[Odeslat]     ││
│                 └──────────────┘│
└─────────────────────────────────┘
```

**Typický průběh:**
1. Tým dostane obrázek skrytý za mřížkou
2. Postupně klikají na políčka → obrázek se odkrývá
3. Za každé odkryté políčko se odečítají body
4. Hráči mohou požádat o nápovědu (odhalení písmen)
5. Cíl: Uhodnout odpověď s maximálním počtem zbývajících bodů
6. **Časový limit:** 10 minut na kolo

---

## 🎮 Příklad Scoring Systému

| Akce | Trestní Body |
|------|---|
| 1. politique odkryté | 0 bodů |
| 2. politčko odkryté | -1 bod |
| 3. politčko odkryté | -2 body |
| 4. politčko odkryté | -3 body |
| ... | ... |
| Chybný pokus odpovědi | -20 bodů |
| Hint - odhalení písmene | -1 až -N bodů |
| **Počáteční body** | **120 bodů** |

Pokud tým uhodne správný odpověď **bez odkryté jediný politik**, získá **120 bodů**.

---

## 🔐 Bezpečnost - Ochrana Odpovědí

Aplikace má **několik vrstev ochrany** aby niemůžlo snadně zjistit správné odpovědi:

### ✅ Implementované Bezpečnostní Prvky

1. **Hashing odpovědí**
   - Odpovědi se ukládají jako **SHA256 hash**
   - V aplikaci se nikdy neobjevuje plaintext odpověď
   - Normalizace: "Steve JÓBS" → "stevejobs" → hash

2. **Anonymizace obrázků**
   - Obrázky jsou pojmenovány: `img_087.jpg`, `img_003.jpg` (ne `steve_jobs.jpg`!)
   - Bez vztahu k otázkám (randomizace mapování)

3. **ZIP archiv**
   - Všechny obrázky jsou zabalené v `assets/images_archive.zip`
   - Čtou se do paměti aplikace (ne jednotlivě na disku)

4. **Offline Admin Data**
   - Plaintext otázky jsou pouze v `original_data/questions_input.json`
   - Po spuštění `prepare_questions.py` se originální obrázky **smažou**
   - Admin si data uchovává v sejfu nebo šifrovaně

Viz: [SECURITY_FAQ.md](SECURITY_FAQ.md) a [docs/design.md](docs/design.md#7-bezpečnost---ochrana-odpovědí)

---

## 📁 Stav Projektu - Co Je Hotovo?

### ✅ **Hotovic - Etapa 1: Analýza & Design**

- [x] Architekturní návrh aplikace
  - Diagram 4 vrstev (Data, Service, Application, Presentation)
  - Detailní component diagram
- [x] Definice všech tříd a zodpovědností
  - Data Models (Question, GameState, Round, ScoreRecord)
  - Services (ScoreManager, AnswerChecker, ImageHandler, TimerService, HintSystem, SecurityService, HintLetterGenerator)
  - Application Layer (GameController, RoundManager)
  - UI Components (MainWindow, RoundScreen, ResultScreen, AdminPanel)
- [x] Datové schéma (JSON formáty)
- [x] Bezpečnostní strategie
  - Hashing + salt
  - Dynamické generování hint_letters
  - Randomizace image_ids
- [x] SOLID principy & testovatelnost

**Výstup:** [docs/design.md](docs/design.md)

### ✅ **Hotové - Admin Nástroje a Návody**

- [x] Script `prepare_questions.py`
  - Normalizace odpovědí
  - SHA256 hashing
  - Randomizace image_ids
  - Vytvoření ZIP archivu
  - Cleanup originálů
- [x] Admin guide pro správu dat
- [x] Security FAQ - odpovědi na bezpečnostní otázky
- [x] Příkladní questions_input.json (10 otázek)

**Výstupy:** 
- [prepare_questions.py](prepare_questions.py)
- [ADMIN_GUIDE.md](ADMIN_GUIDE.md)
- [SECURITY_FAQ.md](SECURITY_FAQ.md)

### 🟡 **Ve Vývoji - Etapa 2: Základní Struktura**

Příští kroky (zatím **NE**):
- [ ] Vytvoření adresářové struktury (`models/`, `services/`, `app/`, `ui/`)
- [ ] Implementace datových modelů 
  - `models/question.py`
  - `models/game_state.py`
  - `models/round.py`
  - `models/score.py`
- [ ] Implementace základních služeb (bez UI)
  - `services/security_service.py`
  - `services/answer_checker.py`
  - `services/score_manager.py`
  - `services/image_handler.py`
  - `services/timer_service.py`
  - `services/hint_system.py`
  - `services/question_loader.py`
- [ ] Unit testy pro služby

### 🔴 **Ještě Nedělané**

- [ ] Etapa 3: Game Engine (herní logika)
- [ ] Etapa 4: GUI (Tkinter)
- [ ] Etapa 5: Zpracování obrázků (maskování, 4×4 dělení)
- [ ] Etapa 6: Bezpečnost (finální implementace)
- [ ] Etapa 7: Testing & Deployment

---

## 📦 Adresářová Struktura

```
informacni_kviz/
│
├── README.md                       ← Tento soubor
├── .github/
│   └── copilot-instructions.md     ← Instrukce pro vývoj
│
├── docs/
│   ├── design.md                   ← Architekturní návrh ✅
│   ├── rules.md                    ← Pravidla scoring (TODO)
│   ├── security.md                 ← Bezpečnost detail (TODO)
│   └── user_guide.md               ← Uživatelský návod (TODO)
│
├── prepare_questions.py            ← Admin script pro přípravu dat ✅
├── ADMIN_GUIDE.md                  ← Námět pro admina ✅
├── SECURITY_FAQ.md                 ← FAQ o bezpečnosti ✅
│
├── original_data/                  ← Pracovní adresář admina
│   ├── questions_input.json        ← Vstupní otázky (plaintext) ✅
│   └── images/                     ← Originální obrázky (TODO)
│
├── data/                           ← Výstupní data (bezpeční)
│   ├── questions.json              ← Otázky s hashy (TODO)
│   ├── config.json                 ← Nastavení aplikace (TODO)
│   └── answers_hash.json           ← Hashe odpovědí (TODO)
│
├── assets/
│   └── images_archive.zip          ← ZIP se všemi obrázky (TODO)
│
├── app/                            ← Application layer (TODO)
│   ├── __init__.py
│   ├── game_controller.py
│   └── round_manager.py
│
├── models/                         ← Data models (TODO)
│   ├── __init__.py
│   ├── question.py
│   ├── game_state.py
│   ├── round.py
│   └── score.py
│
├── services/                       ← Business logic (TODO)
│   ├── __init__.py
│   ├── security_service.py
│   ├── answer_checker.py
│   ├── score_manager.py
│   ├── image_handler.py
│   ├── timer_service.py
│   ├── hint_system.py
│   ├── hint_letter_generator.py
│   └── question_loader.py
│
├── ui/                             ← GUI components (TODO)
│   ├── __init__.py
│   ├── main_window.py
│   ├── round_screen.py
│   ├── result_screen.py
│   ├── admin_panel.py
│   ├── components.py
│   └── theme.py
│
├── tests/                          ← Unit testy (TODO)
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_answer_checker.py
│   ├── test_score_manager.py
│   ├── test_image_handler.py
│   └── test_game_logic.py
│
├── main.py                         ← Vstupní bod aplikace (TODO)
└── requirements.txt                ← Závislosti (TODO)
```

---

## 🚀 Jak Začít?

### Pro Vývojáře

```bash
# 1. Klonuj repository
git clone https://github.com/GeraltOfRiviaa/informacni_kviz.git
cd informacni_kviz

# 2. Přečti design dokument
# → docs/design.md (Architektura)

# 3. Přečti instrukce pro výv
# → .github/copilot-instructions.md (7 etap)

# 4. Pokračuj na Etapu 2
# → Implementace modelů a služeb (bez GUI)
```

### Pro Administrátory (Příprava Dat)

```bash
# 1. Přečti admin návod
# → ADMIN_GUIDE.md

# 2. Připrav otázky
# → Edituj original_data/questions_input.json

# 3. Přidej obrázky  
# → Vlož do original_data/images/

# 4. Spusť přípravu
python prepare_questions.py

# 5. Aplikace je připravena!
# → data/questions.json
# → assets/images_archive.zip
```

---

## 🛠️ Technologické Volby

| Komponenta | Technologie | Status |
|---|---|---|
| **Jazyk** | Python 3.8+ | ✅ |
| **GUI Framework** | Tkinter (doporučeno) | 🔴 TODO |
| **Obrázky** | Pillow (PIL) | 🔴 TODO |
| **Data Format** | JSON | ✅ |
| **Hashing** | hashlib.sha256 | ✅ |
| **Testing** | pytest | 🔴 TODO |
| **Build** | PyInstaller | 🔴 TODO |

---

## 📚 Dokumentace

| Soubor | Obsah | Status |
|---|---|---|
| [docs/design.md](docs/design.md) | Architektura, třídy, API | ✅ |
| [docs/rules.md](docs/rules.md) | Pravidla a scoring | 🔴 TODO |
| [docs/security.md](docs/security.md) | Bezpečnostní detail | 🔴 TODO |
| [docs/user_guide.md](docs/user_guide.md) | Uživatelský návod | 🔴 TODO |
| [ADMIN_GUIDE.md](ADMIN_GUIDE.md) | Příprava otázek | ✅ |
| [SECURITY_FAQ.md](SECURITY_FAQ.md) | FAQ na bezpečnost | ✅ |
| [.github/copilot-instructions.md](.github/copilot-instructions.md) | Instrukce pro vývoj | ✅ |

---

## 🎯 Příští Kroky

### Etapa 2: Základní Projektová Struktura (1-2 týdny)
```
1. Vytvoření adresářové struktury
2. Implementace datových modelů (bez logiky)
3. Implementace service layeru (bez GUI)
4. Unit testy
5. Ověření bezpečnosti
```

### Etapa 3: Herní Logika (2-3 týdny)
```
1. GameController & RoundManager
2. ScoreManager - bodovací logika
3. TimerService - odpočítávání
4. HintSystem - správa nápověd
5. Integration testy
```

### Etapa 4: GUI (3-4 týdny)
```
1. MainWindow - základní layout
2. RoundScreen - herní obrazovka
3. ResultScreen - výsledky
4. AdminPanel - správa
5. Styling & UX
```

### Etapa 5-7: Finish (4-6 týdnů)
```
Image processing, finální bezpečnost, deployment
```

---

## 👥 Požadavky Projektu

### Funkční
- ✅ Načíst obrázky (4×4 mřížka)
- ✅ Odkrývat políčka (s bodovým systémem)
- ✅ Nápovědy (odhalování písmen)
- ✅ Vložení odpovědi
- ✅ Bodování s penalizací
- ✅ Časový limit (10 minut)

### Nefunkční
- ✅ Ochrana odpovědí (SHA256 hash)
- ✅ Bezpečné ukládání dat
- ✅ Uživatelská přívětivost (pro ZŠ)
- ✅ Přehledné GUI (vhodné pro promítání)
- ✅ OOP návrh (SOLID principy)
- ✅ Testovatelnost

---

## 📞 Kontakt & Support

Máte otázky?
- 📖 Podívejte se na [docs/](docs/) složku
- 🔐 Bezpečnost → [SECURITY_FAQ.md](SECURITY_FAQ.md)
- 📝 Příprava dat → [ADMIN_GUIDE.md](ADMIN_GUIDE.md)
- 💻 Vývoj → [.github/copilot-instructions.md](.github/copilot-instructions.md)

---

## 📄 Licence

Projekt je určen pro **vzdělávací účely** (soutěž na základních školách).

---

## 🎓 Cílová Skupina

- **Uživatelé:** Tříčlenné týmy žáků 6.-9. třídy ZŠ
- **Správce:** Učitel nebo organizátor soutěže
- **Vývojář:** Student nebo vývojář se zájmem o školské projekty

---

## 📊 Metriky Projektu

```
Řádků Dokumentace:  ~3000
Řádků Kódu (hotovo): ~900 (prepare_questions.py, nástroje)
Řádků Kódu (TODO):   ~5000 (zbývající implementace)
Etap Vývoje:         7
Aktuální Etapa:      1/7 (100% hotova)
Zbývajících Etap:    6/7 (0% hotovy)

Status: 🟡 Ve Vývoji - Design Hotov, Implementace Začíná
```

---

**Poslední aktualizace:** 24. března 2026  
**Verze:** 0.1.0 (Design Release)

---

> 💡 **Tip:** Pokud chcete po kompletion, začněte čtením [docs/design.md](docs/design.md) aabych se Vám zobrazil jak se systém strukturuje.
