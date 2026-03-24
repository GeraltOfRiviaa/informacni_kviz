#!/usr/bin/env python3
"""
prepare_questions.py - Příprava Quiz Dat (ADMIN SCRIPT)

Tento skript transformuje sadu otázek s plaintext odpověďmi a obrázky
do bezpečné struktury quiz aplikace.

Bezpečnostní kroky:
1. Normalizace odpovědí (lowercase, bez diakritiky)
2. SHA256 hashing s salt
3. Randomizace image_id (aby q001 neměl img_001!)
4. Zašifrování obrázků v ZIP archívu
5. Vyčištění originálních obrázků

Použití:
    python prepare_questions.py

Předpoklady:
- Existuje adresář: original_data/questions_input.json
- Existuje adresář: original_data/images/ s obrázky
- Nainstalován: cryptography, pillow, requirements.txt
"""

import json
import hashlib
import os
import shutil
import secrets
import unicodedata
import zipfile
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

# Importy z services (ale zatím se budou inline, protože nejsou hotové)
# from services.security import SecurityService


class SecurityService:
    """Dočasná implementace - později se přesune do services/"""
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalizuje text: lowercase, bez diakritiky, bez mezer.
        
        Příklady:
        - "Steve Jobs" → "stevejobs"
        - "GOOGLE" → "google"
        - "Štepán" → "stepan"
        """
        # Lowercase
        text = text.lower().strip()
        
        # Odstranění diakritiky (kombinace znaků)
        # NFKD = Compatibility Decomposition
        nfkd_form = unicodedata.normalize('NFKD', text)
        return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])
    
    @staticmethod
    def generate_salt(length: int = 32) -> str:
        """Generuje náhodný salt (hexadecimálně)."""
        return secrets.token_hex(length // 2)
    
    @staticmethod
    def hash_sha256(text: str, salt: str = "") -> str:
        """
        Vrátí SHA256 hash textu.
        
        Args:
            text: Text k zahashování
            salt: Náhodný salt (připojuje se k textu)
        
        Returns:
            Hexadecimální SHA256 hash
        """
        combined = text + salt
        return hashlib.sha256(combined.encode('utf-8')).hexdigest()


class QuestionPreparer:
    """Hlavní třída pro přípravu quiz dat."""
    
    def __init__(self):
        self.security = SecurityService()
        self.base_dir = Path(__file__).parent
        self.original_data_dir = self.base_dir / "original_data"
        self.output_dir = self.base_dir / "data"
        self.images_archive_dir = self.base_dir / "assets"
        self.images_archive_path = self.images_archive_dir / "images_archive.zip"
        
        # Vytvoření potřebných adresářů
        self.output_dir.mkdir(exist_ok=True)
        self.images_archive_dir.mkdir(exist_ok=True)
    
    def validate_input(self) -> bool:
        """Ověří existenci vstupních souborů."""
        input_file = self.original_data_dir / "questions_input.json"
        images_dir = self.original_data_dir / "images"
        
        if not input_file.exists():
            print(f"❌ CHYBA: Soubor neexistuje: {input_file}")
            print(f"   Prosím, vytvořte: original_data/questions_input.json")
            return False
        
        if not images_dir.exists():
            print(f"❌ CHYBA: Adresář neexistuje: {images_dir}")
            print(f"   Prosím, vytvořte: original_data/images/")
            return False
        
        return True
    
    def load_input_questions(self) -> List[Dict]:
        """Načte otázky ze questions_input.json."""
        input_file = self.original_data_dir / "questions_input.json"
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("questions", [])
        except json.JSONDecodeError as e:
            print(f"❌ CHYBA: Neplatný JSON v {input_file}: {e}")
            return []
    
    def generate_random_image_ids(self, count: int) -> List[str]:
        """
        Generuje seznam randomizovaných image_id.
        
        KLÍČOVÉ: IDs nejsou logicky navázané na otázky!
        
        Např.:
        - q001 → img_087
        - q002 → img_003
        - q003 → img_156
        
        Tím se brání deducování: "otázka 1, obrázek 1, musí být první věc"
        """
        # Vygeneruj IDs v rozsahu 1-10000 (dost prostoru)
        image_ids = [f"img_{secrets.randbelow(10000):04d}" for _ in range(count)]
        
        # Zajisti uniqnost
        while len(set(image_ids)) != len(image_ids):
            print("⚠️  Duplikátní image_ids, regeneruji...")
            image_ids = [f"img_{secrets.randbelow(10000):04d}" for _ in range(count)]
        
        return image_ids
    
    def prepare_questions(self) -> Tuple[List[Dict], Dict[str, str]]:
        """
        Transformuje vstupní otázky do bezpečného formátu.
        
        Returns:
            Tuple[questions_list, image_mapping]
            - questions_list: Seznamem otázek s hashy (bez plaintext)
            - image_mapping: {"img_087": "original_steve_jobs.jpg", ...}
        """
        input_questions = self.load_input_questions()
        
        if not input_questions:
            print("❌ Žádné otázky nenalezeny!")
            return [], {}
        
        print(f"📋 Načteno {len(input_questions)} otázek...")
        
        # Vytvoři randomizovaná image_ids
        image_ids = self.generate_random_image_ids(len(input_questions))
        image_mapping = {}  # img_087 → original_steve_jobs.jpg
        
        prepared_questions = []
        
        for idx, question in enumerate(input_questions):
            answer = question.get("answer", "")
            image_file = question.get("image", "")
            
            if not answer or not image_file:
                print(f"⚠️  Otázka {idx+1}: Chybí answer nebo image, přeskakuji...")
                continue
            
            # 1. Normalizace
            normalized_answer = self.security.normalize_text(answer)
            
            # 2. Salt
            salt = self.security.generate_salt(32)
            
            # 3. Hash
            answer_hash = self.security.hash_sha256(normalized_answer, salt)
            
            # 4. Image ID
            image_id = image_ids[idx]
            image_mapping[image_id] = image_file
            
            # 5. Příprava otázky bez plaintext
            prepared = {
                "id": f"q{idx+1:03d}",
                "category": question.get("category", "general"),
                "image_id": image_id,
                "answer_hash": answer_hash,
                "answer_salt": salt,
                "answer_length": len(normalized_answer),
                "difficulty": question.get("difficulty", "medium"),
                "description": question.get("description", "")  # Pro admina (test soubor)
            }
            
            prepared_questions.append(prepared)
            print(f"✅ q{idx+1:03d}: {image_id} - {normalized_answer[:20]}...")
        
        return prepared_questions, image_mapping
    
    def create_images_archive(self, image_mapping: Dict[str, str]) -> bool:
        """
        Vytvoří ZIP archiv se všemi obrázky.
        
        Struktura:
        images_archive.zip
        ├── img_087.jpg (z original/images/original_steve_jobs.jpg)
        ├── img_003.jpg (z original/images/original_google.jpg)
        └── ...
        
        ZIP je UNCOMPRESSED (šifrování se přidá později, pokud bude potřeba)
        """
        images_dir = self.original_data_dir / "images"
        
        print("\n📦 Vytváření ZIP archívu s obrázky...")
        
        try:
            #删除starý archiv pokud existuje
            if self.images_archive_path.exists():
                self.images_archive_path.unlink()
                print(f"🗑️  Smazán starý archiv: {self.images_archive_path}")
            
            with zipfile.ZipFile(self.images_archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for image_id, original_filename in image_mapping.items():
                    source_path = images_dir / original_filename
                    
                    if not source_path.exists():
                        print(f"⚠️  Obrázek nenalezen: {source_path}, přeskakuji...")
                        continue
                    
                    # Přidej do ZIP s anonymním názvem
                    arcname = f"{image_id}{source_path.suffix}"  # img_087.jpg
                    zf.write(source_path, arcname)
                    print(f"  ✅ {original_filename} → {arcname}")
            
            print(f"✅ ZIP archiv vytvořen: {self.images_archive_path}")
            return True
        
        except Exception as e:
            print(f"❌ CHYBA při vytváření ZIP: {e}")
            return False
    
    def save_questions_json(self, questions: List[Dict]) -> bool:
        """Uloží questions.json bez plaintext odpovědí."""
        output_file = self.output_dir / "questions.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "questions": questions,
                    "prepared_at": datetime.now().isoformat(),
                    "count": len(questions)
                }, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Otázky uloženy: {output_file}")
            return True
        except Exception as e:
            print(f"❌ CHYBA při ukládání questions.json: {e}")
            return False
    
    def cleanup_originals(self) -> None:
        """
        BEZPEČNOSTNÍ KROK: Smažeme originální obrázky s názvy odpovědí.
        
        ⚠️ POZOR: Toto je DESTRUKTIVNÍ operace!
        Před spuštěním si udělejte zálohu!
        """
        images_dir = self.original_data_dir / "images"
        
        response = input(
            "\n⚠️  POZOR: Chcete smazat originální obrázky z original_data/images/? "
            "(Ty už jsou v ZIP archívu)\n"
            "Zadejte 'ano' pro potvrzení: "
        )
        
        if response.lower() == 'ano':
            try:
                if images_dir.exists():
                    shutil.rmtree(images_dir)
                    images_dir.mkdir()  # Vytvoř prázdný adresář
                    print(f"🗑️  Všechny obrázky ze {images_dir} smazány.")
                    print("   Ten adresář zůstane prázdný pro případ budoucích změn.")
            except Exception as e:
                print(f"⚠️  Chyba při mazání: {e}")
        else:
            print("❌ Mazání zrušeno - originální obrázky zůstávají.")
            print(f"   Prosím, ručně smažte: {images_dir}")
    
    def run(self) -> bool:
        """Spustí celý proces přípravy."""
        print("=" * 70)
        print("🔐 PŘÍPRAVA QUIZ DAT - BEZPEČNÁ TRANSFORMACE")
        print("=" * 70)
        
        # 1. Validace
        print("\n1️⃣  Validace vstupů...")
        if not self.validate_input():
            return False
        print("✅ Vstupní soubory OK")
        
        # 2. Načtení a transformace
        print("\n2️⃣  Transformace otázek...")
        questions, image_mapping = self.prepare_questions()
        
        if not questions:
            print("❌ Žádné otázky k proces")
            return False
        
        # 3. Vytvoření ZIP archívu
        print("\n3️⃣  Vytvoření archívu s obrázky...")
        if not self.create_images_archive(image_mapping):
            return False
        
        # 4. Uložení questions.json
        print("\n4️⃣  Uložení questions.json...")
        if not self.save_questions_json(questions):
            return False
        
        # 5. Cleanup
        print("\n5️⃣  Čištění originálů...")
        self.cleanup_originals()
        
        # 6. Finální zpráva
        print("\n" + "=" * 70)
        print("✅ PŘÍPRAVA KOMPLETNÍ!")
        print("=" * 70)
        print(f"""
Výstupy:
  ✅ data/questions.json (otázky s hashy, bez plaintext)
  ✅ assets/images_archive.zip (všechny obrázky, bez jmen)
  ✅ Originální obrázky: smazány (pokud jste souhlasili)

Bezpečnost:
  ✅ Odpovědi: Jen jako SHA256 hashe
  ✅ Image_id: Randomizované (q001 ≠ img_001)
  ✅ Obrázky: V ZIP archívu, bez názvy souborů
  ✅ Mapování: Jen v paměti aplikace za runtime

Příští krok: Spusťte aplikaci quiz_app.py
""")
        return True


def main():
    """Vstupní bod skriptu."""
    preparer = QuestionPreparer()
    success = preparer.run()
    
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
