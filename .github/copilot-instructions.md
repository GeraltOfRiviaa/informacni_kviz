# Interaktivní Soutěžní Aplikace - Instrukce pro Vývoj

## Přehled Projektu

Vyvíjíte **znalostní soutěžní aplikaci** v Pythonu pro tříčlenné týmy žáků základních škol.

**Hlavní koncept:**
- Obrázek (osobnost, logo, zařízení, historická fotografie) je skryt za mřížkou 4×4 políček
- Soutěžící postupně odkrývají políčka (za body) a otrzymují písmenové nápovědy
- Cíl: uhodnout, co je na obrázku (jméno, název, pojmenování)
- Scoring: Počet bodů se snižuje za odkryté políčka a nápovědy
- Časový limit: obvykle 10 minut na kolo

---

## Jednotlivé Etapy Vývoje

### 📋 **Etapa 1: Analýza a Návrh Aplikace**
**Cíl:** Vytvořit architektonický návrh a specifikaci aplikace.

**Co se má vytvořit:**
- [ ] Schéma databázové struktury (JSON, SQLite apod.)
- [ ] Diagram GUI aplikace (layout, komponenty)
- [ ] Definice tříd a jejich zodpovědnosti
- [ ] Specifikace API pro jednotlivé funkce
- [ ] Návrh scoring systému (tabulka bodů)

**Výstupy:**
- Dokumentace `docs/design.md` nebo soubor ve formátu, co si zvolíte
- Soupis všech tříd, metod a jejich účelu
- Schéma databáze (pokud se bude používat)

**Poznámky pro Copilota:**
- Zaměřte se čistotě kódu a SOLID principech
- Připravte design s myslí na testovatelnost
- Zvažte bezpečnost (ochrana odpovědí)

---

### 🏗️ **Etapa 2: Základní Projektová Struktura**
**Cíl:** Vytvořit skeletal strukturu projektu s praktickými třídami.

**Co se má vytvořit:**
- [ ] `quiz_app.py` - hlavní spustitelný soubor
- [ ] `models.py` - datové třídy (Question, Team, GameState)
- [ ] `config.py` - konfigurace (počet bodů, čas, penalizace)
- [ ] `utils.py` - pomocné funkce
- [ ] `requirements.txt` - seznam závislostí
- [ ] `README.md` - popis jak spustit

**Datové třídy:**
- `Question` - obrázek, řešení, písmena
- `GameState` - skóre, odkrytá políčka, zbývající čas
- `Team` - jméno týmu, aktuální skóre
- `Grid` - mřížka 4×4 s maskovacím stavem

**Výstupy:**
- Funkční project s lze spustit (nyní bez GUI)
- Unit testy pro základní třídy

---

### 🎮 **Etapa 3: Herní Logika a Scoring Systém**
**Cíl:** Implementovat core game engine se všemi herními pravidly.

**Co se má vytvořit:**
- [ ] `game_engine.py` - hlavní herní logika
  - Funkce na odhalení políčka (s výpočtem bodů)
  - Funkce na odhalení písmene (s výpočtem bodů)
  - Validace a zpracování odpovědi
  - Kontrola správnosti řešení
- [ ] Scoring systém:
  - 1. odkryté políčko: 0 bodů
  - 2. политчко: −1 bod
  - 3. políčko: −2 body
  - atd. (lineární pokles)
  - Chybná odpověď: −20 bodů
  - Sprinty se označením písmen: −1 až −N bodů
- [ ] Timer a mechanika skončení kola
- [ ] Testovací scénáře

**Výstupy:**
- Plně funkční herní engine
- Testy demonstrující scoring logiku
- Dokumentace pravidel v `docs/rules.md`

---

### 🎨 **Etapa 4: Uživatelské Rozhraní (GUI)**
**Cíl:** Vytvořit přehledné a funkční rozhraní vhodné pro soutěž.

**Co se má vytvořit:**
- [ ] Volba mezi technologií (doporučuji **tkinter** nebo **PySimpleGUI**)
- [ ] Hlavní okno aplikace se třemi sekckami:
  - **Levá část:** Mřížka 4×4 tlačítek (odkryvaná políčka)
  - **Střed:** Velký obrázek (postupně odkrývaný)
  - **Přední část:** Řádek s písmeny řešení + Pole pro napsání odpovědi
- [ ] Ovládací prvky:
  - Skóre a zbývající čas (countdown)
  - Tlačítko "Odeslat odpověď"
  - Tlačítko "Nápověda" (odhalení písmene)
- [ ] Respezentace odkrytého/skrytého stavu políčka (barva, ikona)
- [ ] Čittelný font, kontrast, intuitivnost

**Výstupy:**
- Funkční GUI aplikace
- Screenshots/screencast funkcionalitu
- Keyboard/mouse mapování

---

### 🖼️ **Etapa 5: Správa Obrázků a Maskování**
**Cíl:** Implementovat systém maskování obrázků a jejich správu.

**Co se má vytvořit:**
- [ ] `image_handler.py` - zpracování obrázků:
  - Načtení obrázku z souboru
  - Dělení na mřížku 4×4
  - Maskování jednotlivých políček (pixelová vyrušení, rozmazání)
  - Dynamické odhaloje v reálném čase
- [ ] Struktura složky `images/`:
  - `quiz_1/` - obrázek, řešení.txt, písmena.txt
  - `quiz_2/` - ...
- [ ] Testy pro správné obrázkovýmaskování
- [ ] Optimalizace (velikost obrázků, výkon)

**Výstupy:**
- Plně funkční image processing modul
- Sada testovacích obrázků s metadata
- Dokumentace formátu datový quiz

---

### 🔐 **Etapa 6: Bezpečnost - Ochrana proti Úniku Odpovědí**
**Cíl:** Zajistit, aby obsluha a soutěžící nemohli snadno zjistit správnou odpověď.

**Co se má vytvořit:**
- [ ] Bezpečné uchovávání řešení (-enkryptace, hash)
- [ ] Zákaz zobrazení řešení v paměti aplikace (plaintext)
- [ ] Kontrola que správné odpovědi (case-insensitive, diakritika)
- [ ] Zákaz Debug modu nebo přístupu k source kódu během soutěže
- [ ] Audit log - zaznamenání všech pokusů, odhalení
- [ ] Eventuálně: Buildobaný executable (PyInstaller) aby uživatelé viděli jen .exe

**Výstupy:**
- Bezpečné uchování všech citlivých dat
- Dokumentace bezpečnostních chyb `docs/security.md`
- Encryption pro quiz soubory (pokud potřebuju)

---

### ✅ **Etapa 7: Testování, Ladění a Deployment**
**Cíl:** Zajistit, že je aplikace připravena na skutečné použití v soutěži.

**Co se má vytvořit:**
- [ ] Unit testy pro všechny moduly (minimum 80% coverage)
- [ ] Integrationní testy (celý herní flow)
- [ ] Uživatelské testování (user acceptance testing)
- [ ] Bugfix a optimalizace na základě testů
- [ ] Dokumentace pro obsluhu: `docs/user_guide.md`
- [ ] Build script pro vytvoření standalone aplikace
- [ ] Checklist před soutěží (nastavení, testy, zálohy)

**Výstupy:**
- Plně funkční, testovaná aplikace
- Instalační balíček nebo executable
- Uživatelská příručka a IT dokumentace

---

## Povinné Požadavky Společné pro Všechny Varianty

### 1. Programovací Jazyk a Prostředí
- Aplikace **musí být vytvořena v Pythonu 3.8+**
- GUI volby:
  - **Tkinter** (doporučeno - vestavěný, bez instalace) - ideální pro formuláře, správu kol, přehlednost
  - **Pygame** - pro akčnější zpracování, hernější pocit
  - **CustomTkinter** - modernější GUI
  - Volba technologie musí odpovídat typu projektu

### 2. Objektově Orientovaný Návrh
Projekt **musí** být rozdělen minimálně do několika logických tříd:
- `Game` / `App` - hlavní řízení programu
- `Round` / `QuizRound` - logika jednoho kola
- `QuestionManager` / `TaskManager` - načítání a správa úloh
- `ScoreManager` - bodování, penalizace, čas
- `UI` komponenty - okna, panely, dialogy
- `SecurityManager` - práce s ukrytím nebo kontrolou řešení

**Nepřijatelné:** jeden dlouhý soubor plný funkcí bez struktury

### 3. Externí Datové Soubory
- Otázky, obrázky, odpovědi **nesmí** být napevno zadrátovány v kódu
- Data musí být načítána z externích souborů (JSON, CSV apod.)
- Umožňuje změnu soutěžního obsahu bez zásahu do programu

### 4. Časový Limit
- Aplikace **musí** obsahovat odpočítávání času
- Jasné zobrazení zbývajícího času
- Automatické ukončení kola/hry po vypršení limitu
- Korektní ošetření situace, kdy čas vypršel během akce

### 5. Bodování
- Bodování **musí být** promyšlené a průhledné
- Implementované jako samostatná logika (třída `ScoreManager`)
- Soutěžící vidí výsledek během hry a po jejím skončení
- Musí být jasné, za co se body odečítají/přidělují

### 6. Uživatelská Přívětivost
- Aplikace musí být ovladatelná i pro mladší soutěžící (cílová skupina: ZŠ)
- Přehledná pro organizátora
- Čitelné rozhraní, vizuálně uspořádané, funkčně jednoznačné
- Vhodné pro promítání (čitelnost z větší vzdálenosti, velká tlačítka, kontrast)

### 7. Ochrana Správných Řešení ⚠️ KRITICKÉ
Řešení **nesmí** být snadno zjistitelná pouhým otevřením datového souboru.

**Nepřijatelná řešení:**
- Odpověď v běžném textu v JSON
- Odpověď v komentáři nebo proměnné se zavádějícím názvem
- Jednoduché obrácení textu
- Banální „šifry" snadno odhalitelné

**Přijatelná řešení:**
- Ukládání pouze hashů odpovědí, porovnávání hashů zadaného textu
- Oddělený šifrovaný soubor s daty
- Zakódování dat s jejich načtením za běhu
- Kombinace více technik
- Normalizace odpovědi (bez rozdílu V/v, bez diakritiky, bez mezer) + hash

**Nutné:** Zdůvodnit výhody a limity zvoleného přístupu

### 8. Ošetření Chyb
Program musí korektně reagovat na běžné chyby:
- Chybějící nebo poškozený datový soubor
- Nenalezený obrázek
- Prázdný vstup
- Zadání nepovoleného znaku
- Opakované kliknutí
- Vypršení času během akce
- Nevalidní vstup uživatele

### 9. Dokumentace a Prezentace
Projekt **musí** obsahovat dokumentaci popisující:
- Cíl aplikace
- Zvolenou variantu a její zdůvodnění
- Strukturu projektu a organizaci kódu
- Použité knihovny a jejich role
- Popis všech tříd a jejich zodpovědnosti
- Formát datových souborů
- Způsob bodování (tabulka, vzorce)
- **Způsob ochrany řešení s vysvětlením** ⚠️
- Návod k ovládání (pro uživatele i operátora)

Student také připraví krátkou prezentaci nebo démozápisku programu.

---

## Obecné Požadavky na Kód

- **Python 3.8+** (jako baseline)
- **Type hints** - používejte na všechny funkce
- **Docstrings** - každá třída a veřejná metoda musí mít dokumentaci
- **PEP 8** - dodržujte konvenci
- **Testy** - napište testy na kritické funkce (scoring, validation, answer checking)
- **Error Handling** - ošetřit edge cases (chybné obrázky, timeout, neplatný input)
- **Logging** - zapisovat důležité eventy (spuštění, odpovědi, skóre, chyby)

## Specifické Požadavky pro Variantu A - Soutěžní Puzzle

### Funkční Požadavky - Co Aplikace Musí Umět
- [ ] Načíst obrázek a rozdělit jej na 16 částí (mřížka 4×4)
- [ ] Zobrazit neodhalenou mřížku (zamaskované políčka)
- [ ] Kliknutím odhalovat jednotlivé části obrázku
- [ ] Zobrazit políčka odpovídající znakům tajenky (řešení)
- [ ] Umožnit odhalit vybrané písmeno nebo náhodné písmeno (se snížením bodů)
- [ ] Zadat celé řešení do vstupního pole
- [ ] Vyhodnotit správnost odpovědi **bez přímého odhalení řešení v datech**
- [ ] Počítat body podle počtu a typu použitých nápověd (lineární penalizace)
- [ ] Odečítat vyšší penalizaci za chybný pokus (−20 bodů)
- [ ] Ukončit kolo po správném vyřešení nebo po vypršení času

### Doporučené Rozšíření
- Více úrovní obtížnosti
- Různé typy úloh (osobnost, logo, hardware, programovací jazyk)
- Zvukový doprovod
- Animované odhalování políček
- Žebříček týmů a jejich pokrok
- **Režim pro správce soutěže** - výběr dalšího úkolu bez odhalení řešení soutěžícím

### Doporučené Třídy
- `ImagePuzzle` - zpracování obrázků, dělení na mřížku, maskování
- `HintSystem` - správa nápověd a odhalovaných písmen
- `AnswerChecker` - kontrola správnosti odpovědi (s hashing/encryption)
- `ScoreManager` - bodování podle penalizace
- `Timer` - odpočítávání času
- `RoundScreen` - hlavní obrazovka s mřížkou a obrázkem
- `AdminPanel` - panel pro správce (volba otázky, debug režim)

### Grafické a Uživatelské Požadavky
Aplikace musí působit jako **hotový produkt**, ne technická ukázka.

**Povinné prvky:**
- Úvodní obrazovka s názvem aplikace a stručným návodem
- Zřetelné zobrazení času (countdown)
- Zřetelné zobrazení bodů a stavu hry
- Jednoduché přechody mezi obrazovkami
- Závěrečná obrazovka s výsledkem a detaily bodování

**Doporučené principy:**
- Čitelnost z větší vzdálenosti při promítání
- Dostatečně velká tlačítka (minimálně 50×50 px)
- Kontrastní barvy pro snadné rozlišení stavů
- Srozumitelná práce s chybovými hláškami
- Responzivní design (přizpůsobení různým rozlišením)

## Doporučená Struktura Projektu

```
informacni_kviz/
├── .github/
│   └── copilot-instructions.md          # This file
├── main.py                              # Spuštění programu
├── app/
│   ├── __init__.py
│   ├── game.py                          # Hlavní Game třída
│   ├── round.py                         # Logika jednoho kola
│   └── config.py                        # Konfigurace (čas, body, penalizace)
├── ui/
│   ├── __init__.py
│   ├── main_window.py                   # Hlavní okno
│   ├── round_screen.py                  # Obrazovka s puzzle
│   ├── admin_panel.py                   # Panel pro správce
│   ├── components.py                    # Komponenty (tlačítka, dialogy)
│   └── theme.py                         # Barvy, fonty, styly
├── models/
│   ├── __init__.py
│   ├── question.py                      # Třída Question
│   ├── round.py                         # Třída Round
│   └── score.py                         # Třída ScoreRecord
├── services/
│   ├── __init__.py
│   ├── question_loader.py               # Načítání otázek z JSON
│   ├── image_handler.py                 # Zpracování obrázků (4×4 grid)
│   ├── answer_checker.py                # Ověření odpovědi (BEZPEČNOST)
│   ├── score_manager.py                 # Výpočty bodů
│   └── security.py                      # Hashing, šifrování, normalizace
├── data/
│   ├── questions.json                   # Otázky a metadata
│   ├── config.json                      # Nastavení (čas, body, penalizace)
│   └── answers_hash.json                # Hashe odpovědí (CHRÁNĚNO)
├── assets/
│   ├── images/                          # Obrázky pro otázky
│   │   ├── quiz_1.jpg
│   │   ├── quiz_2.jpg
│   │   └── ...
│   ├── sounds/                          # Zvuky (opcionálně)
│   └── fonts/                           # Vlastní fonty (opcionálně)
├── docs/
│   ├── design.md                        # Architektura a design
│   ├── rules.md                         # Pravidla a bodování
│   ├── security.md                      # Bezpečnost a ochrana
│   ├── user_guide.md                    # Návod pro operátora
│   └── api.md                           # API jednotlivých tříd
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_answer_checker.py           # Testy bezpečnosti!
│   ├── test_score_manager.py
│   ├── test_image_handler.py
│   └── test_game_logic.py
├── requirements.txt                     # Závislosti (Pillow, pytest, atd.)
├── README.md                            # Stručný přehled projektu
└── build/                               # Generované executable (PyInstaller)
```

## Technologické Volby

| Komponenta | Možnost | Doporučení |
|-----------|---------|-----------|
| GUI | tkinter, Pygame, CustomTkinter | **tkinter** (vestavěný) nebo **CustomTkinter** (modernější) |
| Obrázky | PIL/Pillow, OpenCV | **Pillow** (jednoduché, rychlé) |
| Datové soubory | JSON, YAML | **JSON** (jednoduchý start + bezpečnost) |
| Hashing | hashlib | **hashlib.sha256** (vestavěný v Pythonu) |
| Šifrování | cryptography | **cryptography** (pokud potřeba) |
| Testy | pytest, unittest | **pytest** (čitelnější, fixtures) |
| Build | PyInstaller | **PyInstaller** (nejjednodušší, bez instalace Pythonu) |

## Bezpečnost a Utajení Řešení ⚠️ KRITICKÁ ČÁST PROJEKTU

Tato část je pro projekt **velmi důležitá**. Nestačí napsat aplikaci, která „jen funguje" – soutěžní aplikace musí být navržena tak, aby nebylo snadné získat správné odpovědi předem.

### Minimální Bezpečnostní Standard
Student **musí** prokázat, že:
- ✅ Správná odpověď **není** v programu nebo datech uložena v otevřené podobě
- ✅ Běžný uživatel ji **nezjistí** pouhým otevřením souboru
- ✅ Ověření správné odpovědi probíhá **kontrolovaným způsobem**

### Příklad Vhodného Řešení
1. **Normalizace odpovědi:**
   - Bez rozdílu velkých a malých písmen
   - Bez diakritiky (ě → e, š → s, atd.)
   - S odstraněním nadbytečných mezer
   - Příklad: "Steve JÓBS" → "steve jobs"

2. **Hashing:**
   - Spočítejte SHA256 hash normalizované odpovědi
   - V souboru `answers_hash.json` uložte jen hash
   - Při kontrole normalizujete vstup a porovnáte hash
   - Příklad: `hash("steve jobs") == "..."` ✓

3. **Kombinace technik:**
   - Můžete kombinovat hashing s salt (bezpečnější)
   - Možnost oddělené šifrované soutěži dat

### Co Je Naopak NEDOSTATEČNÉ ❌
- ❌ Odpověď uložená jako prostý text v JSON
- ❌ Odpověď skrytá jen v komentáři nebo v proměnné se zavádějícím názvem
- ❌ Jednoduché obrácení textu (`jobs steve` místo `steve jobs`)
- ❌ Banální „šifra" snadno odhalitelná (BASE64, ROT13)
- ❌ Debug režim dostupný během soutěže

### Ověření Bezpečnosti
V testovacích soubory (např. `tests/test_answer_checker.py`) můžete ověřit:
- Že odpověď v datech není v přímé podobě
- Že hashing funguje korektně
- Že normalizace funguje pro různé vstupy

---

## Doporučené Tematické Okruhy Otázek a Úloh

Protože jde o soutěž z **informačních technologií**, je vhodné vybírat obsah z těchto oblastí:

- 👤 **Významné osobnosti IT** - Steve Jobs, Bill Gates, Linus Torvalds, Ada Lovelace
- 🏢 **Loga technologických firem** - Apple, Microsoft, Google, Meta, Amazon, Tesla
- 💻 **Hardware a periferie** - CPU, GPU, SSD, monitor, klávesnice, myš
- 📜 **Historie počítačů** - ENIAC, Apple II, IBM PC, první stránky webu
- 🖥️ **Operační systémy** - Windows, macOS, Linux, Android, iOS
- 🌐 **Internet a web** - HTTP, HTML, DNS, IP adresy, domény, TCP/IP
- 🔐 **Bezpečnost** - hesla, firewall, VPN, šifrování, fising
- 💬 **Programování** - programovací jazyky (Python, Java, C++), IDE, verze-control
- 🤖 **Robotika a AI** - neuronové sítě, ChatGPT, Siri, strojové učení
- 📱 **Slavné aplikace a služby** - WhatsApp, Spotify, Netflix, Instagram, Discord

---

## Jak Pracovat s Tímto Dokumentem

1. **Vyberte si etapu** - např. "Etapa 1: Analýza a Návrh"
2. **Popropřejte si Copilota** - řekněte mu, kterou etapu chcete pracovat a co konkrétně
3. **Pracujte iterativně** - Copilot vám pomůže s kódem, designem, testy
4. **Ověřujte výstupy** - po každé etapě zkontrolujte, co bylo vytvořeno
5. **Posun na další etapu** - až budete spokojeni s Current etapou

## Příklady Pokynů pro Copilota

> "Jsem na Etapě 1. Vymysli detailní návrh databázové struktury pro quiz aplikaci včetně ER diagramu."

> "Etapa 2: Vytvoř základní třídy Data-Models s type hints a dokumentací."

> "Jsem na Etapě 3: Implementuj scoring systém kde první políčko je zdarma, druhé −1, třetí −2, atd. Přidej unit testy."

> "Etapa 4: Vytvoř GUI v tkinteru se třeatřídy sekcemi (mřížka, obrázek, odpověď), countdown timeru a tlačítkem."

> "Jsem na Etapě 5: Vytvoř modul na maskování obrázků (4×4 mřížka, pixelový blur na skrytých políčkách)."

---

## Čeklist Hotovosti Projektu

- [ ] Etapa 1: Design & Analýza kompletní
- [ ] Etapa 2: Projektová struktura a modely
- [ ] Etapa 3: Game engine s scoring
- [ ] Etapa 4: GUI aplikace
- [ ] Etapa 5: Image processing
- [ ] Etapa 6: Bezpečnost
- [ ] Etapa 7: Testy a finalizace
- [ ] Dokumentace kompletní
- [ ] Pilotní test s reálnými uživateli
- [ ] Aplikace připravena na soutěž ✅

---

**Poznámka:** Tato instrukce se bude vyvíjet. Pokud během vývoje zjistíte, že je potřeba upravit design nebo přidat nové požadavky, aktualizujte prosím tento dokument.
