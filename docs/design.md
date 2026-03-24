# Architekturní Návrh - Interaktivní Soutěžní Aplikace

**Verze:** 1.0  
**Datum:** 2026-03-24  
**Stav:** Konceptuální návrh

---

## 1. Přehled Aplikace

### 1.1 Účel
Aplikace **Informační Kvíz** je znalostní soutěž pro tříčlenné týmy žáků základních škol. Základem každého kola je **obrázek skrytý za mřížkou 4×4 políček**, který si soutěžící postupně odkrývají a zároveň zbírají písmenové nápovědy. Cílem je správně uhodnout, co je na obrázku (jméno, název, pojmenování).

### 1.2 Klíčové Charakteristiky
- ✅ **Časově omezená kola** (default: 10 minut)
- ✅ **Bodovací systém** se ztrátami za odhalení a chyby
- ✅ **Bez přístupu k otevřeným řešením** v datech
- ✅ **Přehledné GUI** vhodné pro mladší soutěžící
- ✅ **Admin režim** pro obsluhu soutěže

---

## 2. Architektura na Úrovni Vrstev (Layered Architecture)

Aplikace se skládá ze **4 hlavních vrstev**:

```
┌─────────────────────────────────────┐
│     PRESENTATION LAYER (UI)         │  ← Tkinter/PySimpleGUI GUI
│  (TkinterApp, RoundScreen, Panels)  │
└─────────────────────────────────────┘
              ↕ (komunikace)
┌─────────────────────────────────────┐
│     APPLICATION LAYER (LOGIC)       │  ← Game Engine, Round Controller
│  (GameController, RoundManager)     │
└─────────────────────────────────────┘
              ↕ (komunikace)
┌─────────────────────────────────────┐
│      SERVICE LAYER (DOMAIN)         │  ← Business Logic
│  (ScoreManager, AnswerChecker,      │
│   ImageHandler, TimerService)       │
└─────────────────────────────────────┘
              ↕ (komunikace)
┌─────────────────────────────────────┐
│      DATA ACCESS LAYER (DATA)       │  ← External Files, Models
│  (QuestionLoader, Config, Models)   │
└─────────────────────────────────────┘
```

### Technické Detaily Vrstev

#### **Data Access Layer (Vrstva Dat)**
- Načítá data z externích souborů (JSON)
- Spravuje modely dat (Question, Round, Score)
- Konfigurace aplikace (čas, body, penalizace)
- **Není přístup k otevřeným odpovědím** (jen hashe nebo šifrované)

```
Data Sources:
├── data/questions.json      (otázky bez odpovědí)
├── data/config.json         (nastavení)
├── data/answers_hash.json   (CHRÁNĚNO - hashe odpovědí)
└── assets/images/           (obrázky)
```

#### **Service Layer (Vrstva Služeb)**
- Obsahuje všechnu business logiku
- Nezávislá na GUI a datovém formátu
- Snadno testovatelná

**Klíčové služby:**
- `ScoreManager` - výpočet bodů, penalizace
- `AnswerChecker` - validace odpovědí (s hashing/normalizací)
- `ImageHandler` - zpracování obrázků, 4×4 dělení, maskování
- `TimerService` - odpočítávání a ošetření timeoutu
- `HintSystem` - správa odhalených písmen
- `QuestionLoader` - načítání otázek z JSON
- `SecurityService` - normalizace, hashing, šifrování

#### **Application Layer (Vrstva Aplikace)**
- Řídí průběh hry a kol
- Koordinuje komunikaci mezi vrstvami
- Neobsahuje přímou GUI logiku

**Klíčové komponenty:**
- `GameController` - hlavní řízení aplikace
- `RoundManager` - logika jednoho kola
- `GameState` - stav hry (skóre, čas, odpovědi)

#### **Presentation Layer (Vrstva Prezentace)**
- Tkinter GUI komponenty
- Komunikace s uživatelem
- Deleguje business logiku do service/application layerů

**Hlavní okna:**
- `MainWindow` - úvodní obrazovka, menu
- `RoundScreen` - průběh kola (puzzle, nápovědy, odpověď)
- `ResultScreen` - výsledky kola
- `AdminPanel` - nastavení, výběr otázky

---

## 3. Diagram Komponent a Jejich Interakcí

```
┌─────────────────────────────────────────────────────────────────┐
│                     GUI (Tkinter)                               │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────────┐      │
│  │ MainWindow   │  │ RoundScreen   │  │ ResultScreen     │      │
│  │              │  │               │  │                  │      │
│  │ - úvodní ks  │  │ - 4×4 mřížka  │  │ - skóre          │      │
│  │ - nabídka    │  │ - obrázek     │  │ - detaily        │      │
│  │              │  │ - nápověda    │  │ - další kolo?    │      │
│  └──────┬───────┘  │ - odpověď     │  └──────────────────┘      │
│         │          │ - čas→zdola   │          ↑                 │
│         └──────────┤               ├──────────┘                 │
│                    │ - skóre       │                            │
│                    └───────┬───────┘                            │
└─────────────────────────────┼──────────────────────────────────┘
                              ↓ (deleguje)
┌─────────────────────────────────────────────────────────────────┐
│                  GameController                                 │
│  - Řídí průběh hry                                              │
│  - Koordinuje RoundManager a Services                           │
│  - Spravuje GameState                                           │
└──────────────────────────┬──────────────────────────────────────┘
          ↓ (používá)
┌──────────────────────────────────────────────────────────────────┐
│                   RoundManager                                    │
│  - Logika jednoho kola                                           │
│  - Spravuje Timer, AnswerChecker, HintSystem                     │
│  - Komunikuje se ScoreManager                                    │
└──────────────────────────────────────────────────────────────────┘
          ↓ (používá)
┌─────────────────────────────────────────────────────────────────┐
│                    Services (Domain Logic)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐       │
│  │ ScoreManager │  │AnswerChecker │  │ ImageHandler     │       │
│  │              │  │              │  │                  │       │
│  │ - +/- body   │  │ - validace   │  │ - 4×4 dělení    │       │
│  │ - penalizace │  │ - normalizace│  │ - maskování      │       │
│  │              │  │ - hashing    │  │ - odhalování     │       │
│  └──────────────┘  └──────────────┘  └──────────────────┘       │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐       │
│  │ TimerService │  │ HintSystem   │  │SecurityService   │       │
│  │              │  │              │  │                  │       │
│  │ - odpočet    │  │ - písmena    │  │ - hash           │       │
│  │ - timeout    │  │ - náhodné    │  │ - normalizace    │       │
│  │ - update UI  │  │ - zobrazení  │  │ - šifrování      │       │
│  └──────────────┘  └──────────────┘  └──────────────────┘       │
└──────────────────────────────────────────────────────────────────┘
          ↓ (čte/zapisuje)
┌──────────────────────────────────────────────────────────────────┐
│              Data & Config Layer                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐       │
│  │ QuestionLdr  │  │Config Mgr    │  │ Models           │       │
│  │              │  │              │  │                  │       │
│  │ - JSON parse │  │ - scoring    │  │ - Question       │       │
│  │ - questions  │  │ - time       │  │ - Round          │       │
│  │ - images     │  │ - penalties  │  │ - Score          │       │
│  └──────────────┘  └──────────────┘  └──────────────────┘       │
└──────────────────────────────────────────────────────────────────┘
          ↓
┌──────────────────────────────────────────────────────────────────┐
│              External Data Sources                                │
│  ├── data/questions.json                                         │
│  ├── data/config.json                                            │
│  ├── data/answers_hash.json (CHRÁNĚNO)                          │
│  └── assets/images/                                              │
└──────────────────────────────────────────────────────────────────┘
```

---

## 4. Třídy a Jejich Zodpovědnosti

### 4.1 Data Models (models/)

#### `Question`
```python
class Question:
    """Reprezentuje jednu otázku v soutěži."""
    id: str                      # unikátní ID otázky (např. "q001", "q_personality_003")
    image_id: str                # anonymní ID obrázku, NIKOLI název (viz bezpečnost)
    answer_hash: str             # SHA256 hash normalizované odpovědi
    answer_salt: str             # salt použitý při hashování
    answer_length: int           # délka odpovědi (jen pro zobrazení polí)
    difficulty: str              # "easy", "medium", "hard"
    category: str                # "personality", "logo", "hardware"
    description: str             # popis (SAMOTNÝ PRO ADMINA, ne v otázce)
    
    # POZNÁMKA: hint_letters a image_path se NIKDY neukládají v plaintext!
    # hint_letters se generují dynamicky z answer_hash za běhu (viz HintLetterGenerator)
```

#### `GameState`
```python
class GameState:
    """Spravuje stav běžící hry."""
    current_round: int           # číslo aktuálního kola
    team_name: str               # jméno soutěžícího týmu
    total_score: int             # celkový skór
    time_remaining: int          # zbývající čas v sekundách
    revealed_cells: List[Tuple]  # odhalená políčka (4×4 grid)
    revealed_letters: List[str]  # odhalená písmena
    attempts: int                # počet pokusů
    is_active: bool              # zda je kolo aktivní
```

#### `Round`
```python
class Round:
    """Reprezentuje jedno kolo hry."""
    round_number: int
    question: Question
    start_time: datetime
    end_time: datetime
    team_score: int
    is_completed: bool
    reveal_history: List[Dict]   # audit log odhalení
```

#### `ScoreRecord`
```python
class ScoreRecord:
    """Záznam o bodech v jednom kole."""
    round_number: int
    base_points: int
    cells_revealed: int           # kolik políček odhalen
    penalty_cells: int            # penalizace za políčka
    letters_revealed: int         # kolik písmen
    penalty_letters: int          # penalizace za písmena
    wrong_attempts: int           # špatné pokusy
    penalty_wrong: int            # penalizace za chyby
    final_points: int             # celkové body
```

### 4.2 Service Layer (services/)

#### `ScoreManager`
```python
class ScoreManager:
    """Spravuje bodování."""
    def calculate_cell_penalty(cell_number: int) -> int
        """Vrátí penalizaci za odkrytí N-tého políčka."""
        # Logika: 0, -1, -2, -3, ...
    
    def calculate_letter_penalty(letter_number: int) -> int
        """Vrátí penalizaci za N-té písmeno."""
    
    def calculate_wrong_attempt_penalty() -> int
        """Vrátí penalizaci za špatný pokus."""
    
    def calculate_round_score(history: RevealHistory) -> ScoreRecord
        """Vypočítá celkový skór kola."""
```

#### `AnswerChecker`
```python
class AnswerChecker:
    """Kontroluje správnost odpovědí (BEZPEČNOST)."""
    def normalize_answer(answer: str) -> str
        """Normalizuje odpověď: lowercase, bez diakritiky, bez mezer."""
        # Příklad: "Steve JÓBS" → "stevejobs"
    
    def hash_answer(answer: str, salt: str = "") -> str
        """Vrátí SHA256 hash normalizované odpovědi."""
    
    def verify_answer(user_answer: str, answer_hash: str) -> bool
        """Ověří, zda uživatelská odpověď odpovídá hashu."""
    
    def get_answer_hint(answer_letters: List[str]) -> List[str]
        """Vrátí která písmena jsou v odpovědi (pro nápovědu)."""
```

#### `ImageHandler`
```python
class ImageHandler:
    """Zpracovává obrázky: dělení, maskování, odhalování."""
    def load_image(image_path: str) -> PIL.Image
        """Načte a validuje obrázek."""
    
    def create_grid(image: PIL.Image, grid_size: int = 4) -> List[PIL.Image]
        """Rozdělí obrázek na 4×4 = 16 částí."""
    
    def create_masked_grid(parts: List[PIL.Image]) -> List[PIL.Image]
        """Vytvoří zamaskované (rozmazané) verze všech částí."""
    
    def reveal_cell(grid: List[PIL.Image], cell_index: int) -> PIL.Image
        """Vrátí obrázek s odhalenými políčky až do indexu."""
    
    def get_current_display_image(revealed_indices: List[int]) -> PIL.Image
        """Skonstruuje aktuální obrázek pro zobrazení (mix maskovaných + odkrytých)."""
```

#### `TimerService`
```python
class TimerService:
    """Spravuje odpočítávání času."""
    def __init__(duration_seconds: int)
    
    def start()
        """Spustí odpočítávání."""
    
    def get_remaining_time() -> int
        """Vrátí zbývající čas v sekundách."""
    
    def is_time_expired() -> bool
        """Vrátí True, když čas vypršel."""
    
    def on_time_tick() -> Callable
        """Callback pro každou sekundu (update GUI)."""
    
    def stop()
        """Zastaví odpočítávání."""
```

#### `HintSystem`
```python
class HintSystem:
    """Spravuje nápovědy (odhalení písmen)."""
    def __init__(answer: str, revealed_letters: List[str])
    
    def get_all_letters() -> List[str]
        """Vrátí všechna písmena v odpovědi."""
    
    def reveal_letter(letter: str) -> bool
        """Odhalí konkrétní písmeno, vrátí True pokud nové."""
    
    def reveal_random_letter() -> str
        """Odhalí náhodné dosud skryté písmeno."""
    
    def get_revealed_display() -> str
        """Vrátí odpověď s ___ za skrytá písmena."""
        # Příklad: "Steve ____" → "Steve Jo__"
    
    def is_completed() -> bool
        """Vrátí True, pokud jsou všechna písmena odkryta."""
    
    def get_hint_cost(hint_number: int) -> int
        """Vrátí penalizaci za N-tou nápovědu."""
```

#### `SecurityService`
```python
class SecurityService:
    """Poskytuje bezpečnostní operace."""
    def normalize_text(text: str) -> str
        """Removes diacritics, lowercases, removes whitespace."""
        # ě→e, š→s, č→c, etc.
    
    def hash_sha256(text: str, salt: str = "") -> str
        """Vrátí SHA256 hash textu."""
    
    def generate_salt(length: int = 16) -> str
        """Generuje salt pro hashing."""
    
    def encrypt_data(data: str, key: str) -> str
        """Šifruje data (pokud potřeba)."""
    
    def decrypt_data(encrypted: str, key: str) -> str
        """Dešifruje data."""
```

#### `HintLetterGenerator` ← NOVÉ - BEZPEČNOSTNÍ!
Viz výše (samostatný oddíl).


#### `QuestionLoader`
```python
class QuestionLoader:
    """Načítá otázky z externálních souborů."""
    def load_questions(json_path: str) -> List[Question]
        """Načte seznam otázek z JSON."""
    
    def get_question_by_id(question_id: str) -> Question
        """Vrátí konkrétní otázku."""
    
    def get_all_questions() -> List[Question]
        """Vrátí všechny otázky."""
    
    def validate_questions() -> bool
        """Ověří integritu otázek (existence obrázků, atd.)."""
```

#### `HintLetterGenerator` ← KLÍČOVÁ PRO BEZPEČNOST ⚠️
```python
class HintLetterGenerator:
    """Dynamicky generuje hint_letters z answer_hash.
    
    Důvod: hint_letters NESMÍ být uloženy v plaintext v JSON!
    Jinak by osoba, která vidí JSON, viděla odpověď "steve jobs"
    z ["s", "t", "e", "v", "e"] + answer_length.
    """
    
    def generate_hint_letters(
        answer_hash: str,
        answer_length: int,
        hint_percentage: float = 0.3
    ) -> List[str]:
        """
        Deterministicky generuje hint_letters z hashe.
        
        Postup:
        1. Vezmu answer_hash (např. "a3f5b8c2...")
        2. Vypočítám kolik písmen odhalit: answer_length * hint_percentage
        3. Z hashe deterministicky vyberu indexy písmen k odhalení
        4. Vrátím seznam písmen (bez vyzrazení jaká jsou)
        
        Příklad:
        - input: answer_hash="a3f5b8...", answer_length=11, hint_pct=0.3
        - from_hash: indexy [0, 2, 4, 6, 8] → vezmu 3 (30% z 11)
        - (samotná písmena conhece jen AnswerChecker při ověření)
        - output: ["?", "?", "?"] (abstraktní seznam, NE konkrétní písmena!)
        
        ALTERNATIVNĚ - pokročilý přístup:
        Vrátím si jen POČET písmen k odhalení (int), nikoliv seznam.
        Aplikace pak zná jen "3 písmena k nápovědě" bez jejich identit.
        """
        hint_count = int(answer_length * hint_percentage)
        
        # Deterministically vybrat indexy z hash-u
        hash_int = int(answer_hash[:16], 16)  # prvních 16 znaků hashe → int
        indices = []
        for i in range(answer_length):
            hash_val = (hash_int + i) % 256
            if hash_val < (256 * hint_percentage):
                indices.append(i)
            if len(indices) >= hint_count:
                break
        
        return indices  # Seznam indexů, nikoliv samotných písmen!
```

**Bezpečnostní Poznámky k HintLetterGenerator:**
- ✅ `hint_letters` se NEGENERUJÍ z plaintext odpovědi
- ✅ Vygenerují se **deterministicky z answer_hash**
- ✅ Nikdo se nedozví obsah hint_letters bez znalosti answer_hash  
- ✅ Stejná odpověď (stejný hash) = vždy stejné hint_letters (determinismus)
- ✅ Nelze rekonstruovat odpověď ze hint_letters (hash je jednosměrný)

### 4.3 Application Layer (app/)

#### `GameController`
```python
class GameController:
    """Hlavní řízení aplikace."""
    def __init__(ui: MainWindow, config: Config)
    
    def start_app()
        """Inicializuje aplikaci."""
    
    def start_round(question: Question)
        """Spustí nové kolo."""
    
    def end_round(was_completed: bool)
        """Ukončí aktuální kolo."""
    
    def on_cell_revealed(cell_index: int)
        """Callback - uživatel odkryl políčko."""
    
    def on_hint_requested()
        """Callback - uživatel požádal o nápovědu."""
    
    def on_answer_submitted(answer: str)
        """Callback - uživatel zadal odpověď."""
    
    def get_current_game_state() -> GameState
        """Vrátí aktuální stav hry."""
```

#### `RoundManager`
```python
class RoundManager:
    """Logika jednoho kola."""
    def __init__(question: Question, duration: int)
    
    def initialize_grid()
        """Inicializuje 4×4 grid a obrázek."""
    
    def start_timer()
        """Spustí odpočítávání."""
    
    def reveal_cell(cell_index: int) -> RevealResult
        """Odhalí políčko, vrátí penalizaci."""
    
    def request_hint() -> HintResult
        """Obslouží požadavek na nápovědu."""
    
    def submit_answer(user_answer: str) -> AnswerResult
        """Vyhodnotí zadanou odpověď."""
    
    def get_current_score() -> int
        """Vrátí aktuální skór."""
    
    def is_time_expired() -> bool
        """Vrátí True, je-li čas vypršel."""
    
    def finish() -> RoundSummary
        """Ukončí kolo a vrátí souhrn."""
```

### 4.4 Presentation Layer (ui/)

#### `MainWindow`
```python
class MainWindow:
    """Hlavní okno aplikace."""
    def show_welcome_screen()
        """Zobrazí úvodní obrazovku."""
    
    def show_round_screen(question: Question)
        """Zobrazí obrazovku kola."""
    
    def show_result_screen(summary: RoundSummary)
        """Zobrazí výsledky kola."""
    
    def show_admin_panel()
        """Zobrazí administrátorský panel."""
    
    def on_quit()
        """Obslouží zavření aplikace."""
```

#### `RoundScreen`
```python
class RoundScreen:
    """Obrazovka během kola."""
    def __init__(round_manager: RoundManager)
    
    def display_puzzle()
        """Zobrazí mřížku 4×4 s obrázkem."""
    
    def display_image(image: PIL.Image)
        """Zobrazí aktuální stav obrázku."""
    
    def display_hint_letters(revealed: List[str])
        """Zobrazí nápovědu s písmeny."""
    
    def display_timer(remaining_seconds: int)
        """Zobrazí odpočet času."""
    
    def display_score(current_score: int)
        """Zobrazí aktuální skór."""
    
    def on_cell_click(cell_index: int)
        """Callback - uživatel klikl na políčko."""
    
    def on_hint_button_click()
        """Callback - uživatel klikl na nápovědu."""
    
    def on_submit_answer(user_input: str)
        """Callback - uživatel poslal odpověď."""
```

#### `ResultScreen`
```python
class ResultScreen:
    """Obrazovka s výsledky kola."""
    def display_result(summary: RoundSummary)
        """Zobrazí detaily bodování."""
    
    def show_score_breakdown()
        """Zobrazí rozpis bodů (cells, letters, mistakes)."""
    
    def on_next_round_button()
        """Callback - další kolo."""
    
    def on_back_to_menu_button()
        """Callback - zpět na hlavní menu."""
```

---

## 5. Data Structures (JSON Schéma)

### 5.1 questions.json (Bezpečný Formát)
```json
{
  "questions": [
    {
      "id": "q001",
      "category": "personality",
      "image_id": "img_001",
      "answer_hash": "a3f5b8c2d1e9f4a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9",
      "answer_salt": "x9k2m5n8p1q4r7s0t3u6v9w2x5y8z1a4b7",
      "answer_length": 11,
      "difficulty": "medium",
      "category": "personality"
    },
    {
      "id": "q002",
      "image_id": "img_002",
      "answer_hash": "f7e2c9a4b1d8f3e5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7",
      "answer_salt": "w8j3l6o9q2t5u7v1a4d7g0j3m6p9s2v5",
      "answer_length": 6,
      "difficulty": "easy",
      "category": "logo"
    }
  ]
}
```

**Bezpečnostní Poznámky:**
- ❌ `image_path` NIKDY (by zradilo odpověď)
- ❌ `hint_letters` NIKDY (by zradilo odpověď)
- ❌ `normalized_hint` NIKDY (by byl plaintext odpovědi)
- ✅ Jen `image_id` ("img_001", "img_002") → fyzicky je uložen jako `assets/images/img_001.jpg`
- ✅ Jen `answer_hash` a `answer_salt` → ze kterých se nedá odpověz rekonstruovat
- ✅ `answer_length` je OK (jen počet znaků, není bezpečnostní riziko)

### 5.2 config.json
```json
{
  "scoring": {
    "base_points": 120,
    "cell_penalty_base": 0,
    "cell_penalty_increment": 1,
    "letter_penalty_base": 1,
    "wrong_attempt_penalty": 20,
    "time_limit_seconds": 600
  },
  "game": {
    "grid_size": 4,
    "image_mask_type": "pixelate",
    "image_mask_intensity": 10
  },
  "ui": {
    "window_width": 1200,
    "window_height": 800,
    "font_size_normal": 12,
    "font_size_large": 20,
    "button_width": 60,
    "button_height": 60
  }
}
```

### 5.3 Struktura Obrázků (Bezpečná)
```
assets/images/
├── img_001.jpg      # Bez indície v názvu co je odpověď!
├── img_002.jpg
├── img_003.png
├── img_004.jpg
│   ...
└── img_050.jpg

# POZOR: NIKDY "steven_jobs.jpg", "google_logo.jpg", atd.!
```

**Proč?**
- Názvy jako `steve_jobs.jpg` = jasná odpověď
- Anonymní ID `img_001.jpg` = při analýze se neví co to je
- Mapování probíhá jen v `questions.json` přes `image_id`

---

## 6. Tok Dat - Diagram Scénáře

### Scénář: Uživatel Odkrývá Políčko

```
Uživatel klikne na políčko [4]
           ↓
RoundScreen.on_cell_click(4)
           ↓
GameController.on_cell_revealed(4)
           ↓
RoundManager.reveal_cell(4)
           ├→ ImageHandler.reveal_cell(4)
           │  └→ vytvoří aktuální obrázek
           │
           ├→ ScoreManager.calculate_cell_penalty(4)
           │  └→ vrátí -2 (pro 3. políčko je -2)
           │
           └→ RevealResult { image, penalty, new_score }
           ↓
GameController.update_ui()
           ├→ RoundScreen.display_image(image)
           ├→ RoundScreen.display_score(new_score)
           └→ RoundScreen.refresh_grid_buttons()
```

### Scénář: Uživatel Zadá Odpověď

```
Uživatel napíše "Steve Jobs" a klikne Submit
           ↓
RoundScreen.on_submit_answer("Steve Jobs")
           ↓
GameController.on_answer_submitted("Steve Jobs")
           ↓
RoundManager.submit_answer("Steve Jobs")
           ├→ AnswerChecker.normalize_answer("Steve Jobs")
           │  └→ vrátí "stevejobs"
           │
           ├→ AnswerChecker.hash_answer("stevejobs")
           │  └→ vrátí hash
           │
           ├→ Load answers_hash.json pro q001
           │  └→ porovnaj hash
           │
           └→ AnswerResult { is_correct, final_score, summary }
           ↓
Pokud správně:
  GameController.end_round(was_completed=True)
  └→ zobrazit ResultScreen
```

---

## 7. Bezpečnost - Ochrana Odpovědí (AKTUALIZOVÁNO)

### 7.1 Strategie - 3 Vrstvy Ochrany
1. **Anonymizace Obrázků** - `img_001.jpg` místo `steve_jobs.jpg`
2. **Normalizace + Hashing** - SHA256 hash normalizované odpovědi
3. **Dynamické Generování Nápověd** - hint_letters generují se z hashe, ne z plaintext

### 7.2 Pracovní Postup

#### Při Vytvoření Otázky (prepare_questions.py)
```python
# Máme:
original_answer = "Steve Jobs"

# Krok 1: Normalizace
normalized = SecurityService.normalize_text(original_answer)
# → "stevejobs"

# Krok 2: Generování salt a hash
salt = SecurityService.generate_salt(32)
# → "x9k2m5n8p1q4r7s0t3u6v9w2x5y8z1a4b7"

answer_hash = SecurityService.hash_sha256(normalized + salt)
# → "a3f5b8c2d1e9f4a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9"

# Krok 3: Uloženíím do questions.json (NIKDY ne plaintext!)
questions_entry = {
    "id": "q001",
    "image_id": "img_001",  # ← Anonymní ID!
    "answer_hash": answer_hash,
    "answer_salt": salt,
    "answer_length": len(normalized),  # 9 (bez mezer)
    "difficulty": "medium",
    "category": "personality"
}

# Krok 4: Dynamické generování hint_letters
hint_indices = HintLetterGenerator.generate_hint_letters(
    answer_hash=answer_hash,
    answer_length=9,
    hint_percentage=0.3  # 30% otázky
)
# → [0, 3, 6] (indexy v "stevejobs")

# Krok 5: Obrázek
# Zkopíruj steve_jobs.jpg → img_001.jpg
shutil.copy("original_images/steve_jobs.jpg", "assets/images/img_001.jpg")
# ← Bez indície v názvu!

# ✅ VÝSLEDEK: questions.json obsahuje JEN hash, salt, image_id
# ✅ VÝSLEDEK: Nikdo nevidí "Steve Jobs" ani v JSON, ani v názvech souborů!
```

#### Při Spuštění Hry (runtime)
```python
# 1. Načtení otázky z JSON
question = QuestionLoader.load_question("q001")
# {id, image_id, answer_hash, answer_salt, answer_length, ...}

# 2. Načtení obrázku
image = ImageHandler.load_image(f"assets/images/{question.image_id}.jpg")
# → Obrázek se načte ANONYMNĚ, bez indície

# 3. Generování hint_letters (dynamicky, za běhu)
hint_indices = HintLetterGenerator.generate_hint_letters(
    answer_hash=question.answer_hash,
    answer_length=question.answer_length,
    hint_percentage=0.3
)
# → [0, 3, 6]

# 4. Inicializace HintSystem
hint_system = HintSystem(
    answer_length=question.answer_length,  # ← NIKDY ne plaintext!
    hint_indices=hint_indices,              # ← Indexy k odhalení
    answer_hash=question.answer_hash        # ← Pro pozdější verifikaci
)

# 5. Při kliknutí na hint → HintSystem odhalí písmeno na daném indexu
# ALE: HintSystem NIKDY neví co je za písmenem!
# (To ví jen AnswerChecker při ověření)
```

#### Při Ověření Odpovědi
```python
# Uživatel zadá: "steve jobs" (nebo "STEVE JOBS", "Štěv Jóbs", ...)
user_answer = "STEVE JOBS"

# AnswerChecker vrátí:
is_correct = AnswerChecker.verify_answer(
    user_input=user_answer,
    answer_hash=question.answer_hash,
    answer_salt=question.answer_salt
)

# Interně v verify_answer():
normalized_user = SecurityService.normalize_text(user_answer)
# → "stevejobs"

user_hash = SecurityService.hash_sha256(normalized_user + answer_salt)
# → "a3f5b8c2d1e9f4a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9"

is_match = (user_hash == question.answer_hash)
# → True nebo False
```

### 7.3 Bezpečnostní Matice

| Co | Kde Uloženo | Formát | Vidí Uživatel | Riziko |
|---|---|---|---|---|
| **Odpověď** (plaintext) | NIKDY | N/A | ❌ | ✅ Bezpečné |
| **answer_hash** | questions.json | SHA256(norm.) | Ano, ale bezpečné | ✅ OK (jednosměrný) |
| **answer_salt** | questions.json | Náhodný string | Ano | ✅ OK (je součást design) |
| **answer_length** | questions.json | int | Ano | ✅ OK (neinformativní) |
| **hint_letters** | NIKDY | N/A | ❌ | ✅ Bezpečné |
| **hint_indices** | Paměť (runtime) | List[int] | ❌ (v kódu ano, ale nezradí odpověď) | ✅ Bezpečné |
| **image_path** | NIKDY (anonymní!) | "img_001" | Ano, anonymně | ✅ Bezpečné |
| **image filename** | Disk | "img_001.jpg" | Ano, anonymně | ✅ Bezpečné |

### 7.4 Co Kdyby Někdo Prošetřoval Soubor Aplikace?

**Scénář:** Hackerský pokus - analyza `.exe` (PyInstaller) nebo zdrojového kódu

```
1. Otevře PyInstaller executable (PyInstaller odstraňuje .pyc)
   → Zdrojový kód je ukrytý, ale v memory...
   
2. Podívá se do questions.json
   ✅ Vidí: image_id "img_001", answer_hash, answer_salt
   ❌ Nevidí: Jaká je odpověď!
   
3. Pokusí se dekódovat answer_hash
   ❌ Není možné (SHA256 je jednosměrný)
   ❌ Ani s salt (salt je součást hashes)
   
4. Podívá se do HintSystem kódu
   ✅ Vidí: hint_indices [0, 3, 6]
   ❌ Ale NEVÍ jaké znaky to jsou! (bez plaintext odpovědi)
   
5. Podívá se na obrázky
   ✅ Vidí: "img_001.jpg"
   ❌ Bez jména souboru neví co je na obrázku
   ❌ (A i kdyby věděl, neodhalí to odpověď, jen zadání)
```

### 7.5 Porovnání: Starý Design vs. Nový

| Aspekt | ❌ STARÝ | ✅ NOVÝ |
|---|---|---|
| **image_path** | `"assets/images/steve_jobs.jpg"` | `"img_001.jpg"` |
| **hint_letters** | `["s", "t", "e", "v", "e"]` (v JSON) | Generují se dynamicky z hash |
| **normalized_hint** | `"steve jobs"` (v JSON) | NEEXISTUJE (plaintext by byla zrada) |
| **answer** | `"Steve Jobs"` (v JSON) | NEEXISTUJE (nikdy v plaintext) |
| **answer_hash** | Uložen v separátním souboru | Uložen v questions.json |
| Bezpečnost | ❌ Slabá | ✅ Silná |
| Údržba | Více souborů | Jeden questions.json |

---

### 7.6 Důvody Tohoto Přístupu
- ✅ Odpověď není vidět v plaintext
- ✅ Obrázky jsou anonymizované
- ✅ Hint_letters jsou derivovány, ne hardcoded
- ✅ Salt brání rainbow table útokům
- ✅ Normalizace řeší variace (V/v, diakritika)
- ✅ Jednoduché, efektivní pro školu
- ℹ️ Vyhovuje pro školský projekt

---

### 7.7 Jak Připravit questions.json (Admin Script)

```python
# prepare_questions.py - spuštěno OFFLINE, jenom na počítači admina

import json
import hashlib
import os
from services.security import SecurityService

questions = []
image_counter = 1

# Definice otázek (s plaintext!)
quiz_data = [
    {
        "answer": "Steve Jobs",
        "image_file": "original_images/steve_jobs.jpg",
        "difficulty": "medium"
    },
    {
        "answer": "Google",
        "image_file": "original_images/google_logo.jpg",  
        "difficulty": "easy"
    }
]

for item in quiz_data:
    answer = item["answer"]
    
    # 1. Normalizace
    normalized = SecurityService.normalize_text(answer)
    
    # 2. Salt
    salt = SecurityService.generate_salt(32)
    
    # 3. Hash
    answer_hash = SecurityService.hash_sha256(normalized + salt)
    
    # 4. Image ID
    image_id = f"img_{image_counter:03d}"
    image_counter += 1
    
    # 5. Zkopíruj obrázek
    shutil.copy(
        item["image_file"],
        f"assets/images/{image_id}.jpg"
    )
    
    # 6. Přidej do questions[]
    questions.append({
        "id": f"q{image_counter - 1:03d}",
        "category": "...",  # určíš podle kontextu
        "image_id": image_id,
        "answer_hash": answer_hash,
        "answer_salt": salt,
        "answer_length": len(normalized),
        "difficulty": item["difficulty"]
    })

# 7. Ulož questions.json
with open("data/questions.json", "w") as f:
    json.dump({"questions": questions}, f, indent=2)

print("✅ questions.json připraven bez plaintext odpovědí!")
```

---

---

## 8. SOLID Principy v Návrhu

### Single Responsibility
- `ScoreManager` - zodpovídá jen za bodování
- `ImageHandler` - zodpovídá jen za obrázky
- `AnswerChecker` - zodpovídá jen za validaci
- ✅ Každá třída má jedinou odpovědnost

### Open/Closed
- Služby v `services/` jsou otevřené pro rozšíření (např. nový typ maskování)
- Uzavřené pro modifikaci (měníme jen config.json)

### Liskov Substitution
- Service interfaces lze vzájemně substituovat bez přerušení chování

### Interface Segregation
- GUI komunikuje jen přes veřejné metody ApiController
- Testy si mohou mock-ovat jednotlivé služby nezávisle

### Dependency Injection
- ServiceLocator nebo konstruktor-based DI
- RoundManager přijímá dependencies: `RoundManager(scm, acm, ih, ts)`

---

## 9. Testovatelnost

### Unit Testy (Service Layer)
```
tests/
├── test_score_manager.py
│   ├── test_calculate_cell_penalty
│   ├── test_calculate_wrong_attempt_penalty
│   └── test_calculate_round_score
├── test_answer_checker.py
│   ├── test_normalize_answer
│   ├── test_hash_answer
│   ├── test_verify_answer
│   └── test_diacritics_removal
├── test_image_handler.py
│   ├── test_load_image
│   ├── test_create_grid
│   ├── test_reveal_cell
│   └── test_masked_grid_creation
└── test_hint_system.py
    ├── test_reveal_letter
    ├── test_reveal_random
    └── test_get_revealed_display
```

### Integration Testy (Application Layer)
```
tests/
└── test_round_manager.py
    ├── test_full_round_scenario
    ├── test_timer_expiry
    ├── test_wrong_answer_penalty
    └── test_complete_game_flow
```

### GUI Testy (Manual)
- Screenshoty, user testing scénáře

---

## 10. Roadmap Implementace

| Fáze | Komponenta | Časový Rámec |
|------|-----------|--------------|
| 1    | Models + Config | 1-2 dny |
| 2    | Services (bez GUI) | 2-3 dny |
| 3    | Unit testy | 1-2 dny |
| 4    | Application Layer | 1-2 dny |
| 5    | GUI (Tkinter) | 3-4 dny |
| 6    | Integration | 1-2 dny |
| 7    | Bezpečnost + Testing | 2-3 dny |
| **Celkem** | | **11-18 dní** |

---

## 11. Poznámky k Dalšímu Vývoji

- ✅ Design je **modulární a testovatelný**
- ✅ Snadné rozšíření (nový typ maskování, nové skóre pravidlo)
- ✅ Snadné přepnout na OpenGL či Pygame bez změny business logiky
- ✅ Odpovědi jsou chráněny hashem
- ⚠️ Timer musí běžet v separátním vlákně (threading)
- ⚠️ GUI refresh musí být optimalizovaný (PIL image buffering)

---

**Status:** Schváleno pro implementaci ✅
