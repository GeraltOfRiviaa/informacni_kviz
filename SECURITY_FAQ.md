# Bezpečnostní FAQ

## 1) Proč nejsou odpovědi v prostém textu?

Protože by je šlo snadno přečíst ze souboru. V aplikaci se ukládá jen:

- `answer_hash`
- `answer_salt`
- metadata (`difficulty`, `category`, `image_id`)

Ověření probíhá porovnáním hashe normalizovaného vstupu s uloženým hashem.

## 2) Je bezpečné mít obrázky jako normální soubory?

Ano, v tomto projektu je kritické tajemství odpovědí, ne samotný obrázek. Obrázek je stejně hráči zobrazen během hry.

Bezpečnost je zajištěna takto:

- `image_id` je anonymní (`img_XXXX`)
- mapování mezi autorským názvem a runtime názvem se generuje při přípravě dat
- plaintext odpověď není v runtime datech

## 3) Co přesně dělá normalizace odpovědi?

Před hashováním se odpověď:

- převede na malá písmena
- odstrani diakritika
- sjednotí mezery

Příklad:

- `"Steve   JÓBS"` -> `"steve jobs"`

## 4) Co když uživatel zkusí útok hrubou silou?

Admin přihlášení má omezení počtu pokusů (uzamčení po neúspěšných pokusech). U odpovědí v kvízu je útok hrubou silou v praxi omezen časem kola a herním UX.

## 5) Co když chybí obrázek?

`ImageHandler` vytvoří placeholder jen pro defaultní runtime složku `assets/images/`, aby GUI nespadlo. To je provozní ochrana dostupnosti, ne bezpečnostní bypass.

## 6) Co je minimum před reálnou soutěží?

- změnit výchozí heslo správce
- projít `PRE_DEPLOYMENT_CHECKLIST.md`
- potvrdit, že `data/questions.json` neobsahuje pole `answer` v plaintextu
- doplnit reálné obrázky místo placeholderu

## 7) Je potřeba šifrovat i obrázky?

Pro školní offline použití obvykle ne. Pokud to chcete zpřísnit, lze přidat šifrovanou distribuci dat, ale pro správnost soutěže je zásadní ochrana odpovědí (hash+salt), ne skrytí obrázků.
