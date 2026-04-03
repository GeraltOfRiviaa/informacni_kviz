# Průvodce Správce

Praktický návod pro přípravu otázek a obrázků bez ZIP archivu.

## Cíle

- připravit nové kolo soutěže bez zásahu do kódu
- uložit odpovědi bez plaintextu
- naplnit runtime složku `assets/images/`

## Vstupy

- `original_data/questions_input.json`
- obrázky v `original_data/images/`

### Formát questions_input.json

```json
{
  "questions": [
    {
      "answer": "Microsoft",
      "image": "img_005.jpg",
      "category": "logo",
      "difficulty": "easy",
      "description": "Společnost za Windows a Office"
    }
  ]
}
```

Povinné je `answer` a `image`.

## Postup

1. Vlož obrázky do `original_data/images/`
2. Uprav `original_data/questions_input.json`
3. Spust:

```bash
python prepare_questions.py
```

4. Zkontroluj výstup:

- `data/questions.json`
- soubory v `assets/images/` s názvy `img_XXXX.ext`

## Co skript dělá

- normalizuje odpověď (`lower`, bez diakritiky)
- vygeneruje `salt`
- vypočítá SHA256 hash
- přiřadí náhodný `image_id` (`img_1234`)
- zkopíruje obrázek do `assets/images/` pod anonymním názvem
- odstraní starý `assets/images_archive.zip`, pokud existuje

## Když chybí obrázek

Když je v `questions_input.json` obrázek, který neexistuje, skript vytvoří placeholder obrázek. Aplikace zůstane spustitelná, ale před soutěží doplňte reálné soubory.

## Kontrolní seznam před soutěží

- `python main.py` se spustí bez chyby
- pro každou otázku existuje odpovídající soubor v `assets/images/`
- v `data/questions.json` nejsou plaintext odpovědi
- admin heslo je změněné z výchozí hodnoty

## Doporučení

- Udržujte zálohu `original_data/`
- Pro produkci nepoužívejte testovací nebo placeholder obrázky
- Používejte konzistentní rozlišení (např. 1280x720 nebo 960x540)
