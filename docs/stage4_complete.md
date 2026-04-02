# Etapa 4: Uživatelské Rozhraní (GUI) - Hotovo ✅

## Přehled Etapy 4

Etapa 4 implementuje kompletní Tkinter-based GUI pro soutěžní aplikaci. Aplikace má dva hauptní režimy:

1. **Admin Panel** - Výběr otázek bez odhalení odpovědí
2. **Round Screen** - Chod hry s puzzle, odpověďmi a bodováním

### Technologie

- **Framework**: Tkinter (vestavěný, bez instalace)
- **Python**: 3.8+
- **Architektura**: Modular component-based design
- **Threading**: Background timer updates

---

## Struktura UI Modulu

```
ui/
├── __init__.py           # UI package exports
├── theme.py              # Colors, fonts, dimensions (centralized design)
├── components.py         # Reusable UI widgets
├── round_screen.py       # Main gameplay interface
├── admin_panel.py        # Question selection interface
└── styles.py             # (Optional) Advanced styling

gui.py                     # Main application entry point
main.py                    # Updated to launch GUI
```

---

## Komponenty

### 1. Theme (`ui/theme.py`)

Centrální definice všech vizuálních prvků:

```python
COLORS = {
    "bg_primary": "#1e1e1e",      # Main dark background
    "bg_secondary": "#2d2d2d",    # Slightly lighter
    "accent": "#0078d4",          # Blue accent
    "success": "#107c10",         # Green (correct)
    "danger": "#e81123",          # Red (error)
    ...
}

FONTS = {
    "title": ("Arial", 24, "bold"),
    "heading": ("Arial", 16, "bold"),
    "body": ("Arial", 12),
    ...
}
```

### 2. Reusable Components (`ui/components.py`)

#### ModernButton
- Hover effects s barevnými přechody
- Customizable colors
- Kód: ~50 řádků

```python
ModernButton(
    parent,
    "Click Me",
    command=callback,
    bg_color=COLORS["success"],
    width=12
)
```

#### GridButton
- Jeden prvek 4×4 mřížky
- Callendní state (hidden/revealed)
- Kód: ~35 řádků

```python
button = GridButton(parent, grid_index=5)
button.reveal()  # Mark as revealed
```

#### TimerWidget
- Zobrazení odpočítávaného času (MM:SS)
- Barva se mění podle času (zelená→oranž→červená)
- Kód: ~30 řádků

```python
timer = TimerWidget(parent)
timer.update_time(150)  # 2:30
```

#### ScoreDisplay
- Zobrazení aktuálního skóre
- Dynamická aktualizace
- Kód: ~25 řádků

#### HintDisplay
- Zobrazení prozatím odhalených písmen
- Format: "S_eve J_bs"
- Kód: ~30 řádků

#### InputField
- Text input pro odpověď hráče
- Enter key pro submit
- Kód: ~35 řádků

### 3. Puzzle Grid (`ui/round_screen.py` - PuzzleGrid)

```python
class PuzzleGrid(tk.Frame):
    def __init__(self, parent, on_cell_click=None):
        # Vytvoří 4×4 grid tlačítek
        # Každé tlačítko je GridButton s indexem 0-15

    def reveal_cell(self, index):
        # Odhalí jednu buňku

    def get_revealed_count():
        # Počet odhalených buněk
```

### 4. Round Screen (`ui/round_screen.py` - RoundScreen)

Hlavní herní obrazovka. Má 3-části layout:

```
┌──────────────────────────────────────────┐
│ Time: 02:30  │  Score: 150  │  Category  │
├────────────────────────────────────────  │
│ Grid 4×4   │  Image Display  │  Hints    │
│ (cells)    │  (placeholder)  │  Letters  │
│            │                 │  & Stats  │
├────────────────────────────────────────  │
│ [Input field] │ Submit | Hint | Quit    │
└──────────────────────────────────────────┘
```

**Funkce:**
- Zobrazuje puzzle mřížku s klikáním
- Ukázuje obrázek (zatím placeholder)
- Umožňuje odhalovat písmena (nápovědy)
- Přijímá odpověď hráče
- Aktualizuje skóre v reálném čase
- Spravuje timer s countdown

**Klíčové metody:**
```python
update_timer(remaining_seconds)      # Aktualizuj timer display
_handle_cell_click(index)            # Uživatel klikl na buňku
_handle_hint_button()                # Nápověda
_submit_answer(answer)               # Vyhodnoť odpověď
```

### 5. Admin Panel (`ui/admin_panel.py`)

Obrazovka pro výběr otázek bez odhalení odpovědí.

**Funkce:**
- Filtrování otázek: kategorie, obtížnost
- Náhled otázky (bez odpovědi!)
- Spuštění kola s vybranou otázkou
- Zabezpečení: Odpověď nikdy není zobrazena

**Bezpečnost:**
```python
# Admin vidí:
self.preview_id = "q123"
self.preview_category = "Osobnosti"
self.preview_difficulty = "Medium"
self.preview_length = "11"

# Admin NEVÍDÍ:
# - The actual answer (NIKDY!)
# - Answer hash
# - Answer salt
```

---

## Hlavní Aplikace (`gui.py` - QuizApplication)

Řídí screen management a game flow:

```python
class QuizApplication:
    def __init__(self, root: tk.Tk):
        self.quiz_app = QuizApp()  # Game controller
        self.show_admin_panel()

    def show_admin_panel(self):
        # Zobraz výběr otázek

    def _on_start_round(self, question):
        # Uživatel vybral otázku, začni hru
        round_manager = self.quiz_app.start_round(question)
        round_manager.start()
        self.show_round_screen(round_manager)
        self._start_timer_thread(round_manager)  # Background timer

    def show_round_screen(self, round_manager):
        # Zobraz herní obrazovku

    def show_results(self, score_record):
        # Zobraz výsledky

    def _timer_loop(self):
        # Background thread: aktualizuje timer každých 100ms
        # Volá round_manager.update_time()
        # Detekuje timeout
```

---

## Integration s Existujícím Services

GUI se integruje s existujícím RoundManager:

```python
# AdminPanel → QuizApplication
question = admin_panel.selected_question
↓
# QuizApplication → QuizApp → RoundManager
round_manager = quiz_app.start_round(question)
round_manager.start()
↓
# RoundScreen → RoundManager calls
round_manager.reveal_cell(index)   # Uživatel klikl na buňku
round_manager.request_hint_random()  # Nápověda
round_manager.check_answer(text)   # Kontrola odpovědi
round_manager.finalize(is_correct) # Konec kola
↓
# Vrátí ScoreRecord
score_record = round_manager.get_final_score()
display_results(score_record)
```

---

## Spuštění

```bash
# Spuštění aplikace
python main.py

# Nebo přímo
python gui.py

# Spuštění testů
python -m pytest tests/test_ui_components.py -v

# Všechny testy
python -m pytest tests/ -q
```

---

## Test Výsledky Etapa 4

```
tests/test_ui_components.py::TestModernButton::test_button_creation PASSED
tests/test_ui_components.py::TestModernButton::test_button_command PASSED
tests/test_ui_components.py::TestGridButton::test_grid_button_creation PASSED
tests/test_ui_components.py::TestGridButton::test_grid_button_reveal PASSED
tests/test_ui_components.py::TestTimerWidget::test_timer_creation PASSED
tests/test_ui_components.py::TestTimerWidget::test_timer_update PASSED
tests/test_ui_components.py::TestTimerWidget::test_timer_color_green PASSED
tests/test_ui_components.py::TestTimerWidget::test_timer_color_orange PASSED
tests/test_ui_components.py::TestTimerWidget::test_timer_color_red PASSED
tests/test_ui_components.py::TestScoreDisplay::test_score_creation PASSED
tests/test_ui_components.py::TestScoreDisplay::test_score_update PASSED
tests/test_ui_components.py::TestHintDisplay::test_hint_creation PASSED
tests/test_ui_components.py::TestHintDisplay::test_hint_update PASSED
tests/test_ui_components.py::TestInputField::test_input_creation PASSED
tests/test_ui_components.py::TestInputField::test_input_get_text PASSED
tests/test_ui_components.py::TestInputField::test_input_clear PASSED
tests/test_ui_components.py::TestPuzzleGrid::test_grid_creation PASSED
tests/test_ui_components.py::TestPuzzleGrid::test_grid_cell_reveal PASSED
tests/test_ui_components.py::TestPuzzleGrid::test_grid_revealed_count PASSED
tests/test_ui_components.py::TestPuzzleGrid::test_grid_cell_click PASSED
tests/test_ui_components.py::TestTheme::test_colors_exist PASSED
tests/test_ui_components.py::TestTheme::test_fonts_exist PASSED

22 passed in 2.47s
```

### Celkem: **145 testů** ✅

- Etapa 2: 51 testů
- Etapa 3: 72 testů
- Etapa 4: 22 testů

---

## Bezpečnost

✅ **Odpovědi nejsou nikdy viditelné v Admin Panelu**

```python
# admin_panel.py - preview metoda
self.preview_id.config(text=question.id)
self.preview_category.config(text=question.category)
self.preview_difficulty.config(text=question.difficulty)
self.preview_length.config(text=question.answer_length)

# NIKDY:
# self.preview_answer.config(text=question.answer)  ← NEDĚLEJ TO!
```

---

## Architektura GUI

```
QuizApplication (Main Window)
├── AdminPanel (Screen 1)
│   ├── Question List
│   ├── Filters (Category, Difficulty)
│   ├── Preview (WITHOUT answer)
│   └── Buttons (Start, Quit)
│
└── RoundScreen (Screen 2)
    ├── Top Bar (Timer, Score, Category)
    ├── Main Area
    │   ├── Puzzle Grid (4×4)
    │   ├── Image Display
    │   └── Hint Display
    └── Bottom Bar (Input, Buttons)
```

### Threading Model

```
Main Thread (Tkinter event loop)
└── GUI Updates
    └── Button clicks, screen changes

Background Timer Thread
├── Updates timer every 100ms
├── Calls round_manager.update_time()
├── Schedules main thread updates via root.after()
└── Detects timeout
```

---

## Design Principy

1. **Separation of Concerns**: GUI (ui/) vs. Logic (services, models)
2. **Reusable Components**: theme.py pro centrální design
3. **Security First**: Odpovědi nikdy nejsou viditelné
4. **User-Friendly**: Velké tlačítka, čitatelné písmo, kontrast
5. **Responsive**: Timer updates bez zamrzení UI
6. **Type-Safe**: Type hints na všech metodách

---

## Příští Kroky: Etapa 5

Etapa 5 bude fokus na:
1. **Image Processing**: Rozdělit obrázek na 4×4 grid
2. **Image Masking**: Pixelovat/rozmazat skryté buňky
3. **Integration**: Zobrazit obrázek v RoundScreen

---

## Shrnutí Hotovosti

| Etapa | Komponenta | Status | Testy |
|-------|-----------|--------|-------|
| 1 | Návrh | ✅ | - |
| 2 | Models, Config | ✅ | 51/51 |
| 3 | Services | ✅ | 72 |
| 4 | GUI (Tkinter) | ✅ | 22 |
| 5 | Image Processing | ⏳ | - |
| 6 | Security | ⏳ | - |
| 7 | Tests, Deploy | ⏳ | - |

**Status:** 4 z 7 etap hotovo (57%) 🎯
