#!/usr/bin/env python3
"""
prepare_questions.py - Admin script for preparing quiz data.

This script transforms plaintext authoring input into runtime-safe quiz data:
1. Normalize and hash answers (SHA256 + salt)
2. Randomize image_id values
3. Copy images to assets/images using anonymized names
4. Optionally clean original source images

Usage:
    python prepare_questions.py
"""

import hashlib
import json
import secrets
import shutil
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from PIL import Image, ImageDraw


class SecurityService:
    """Small helper for answer normalization and hashing."""

    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize to lowercase without diacritics and extra spaces."""
        normalized = text.lower().strip()
        normalized = " ".join(normalized.split())
        nfkd = unicodedata.normalize("NFKD", normalized)
        return "".join(c for c in nfkd if not unicodedata.combining(c))

    @staticmethod
    def generate_salt(length: int = 32) -> str:
        """Generate random hex salt."""
        return secrets.token_hex(length // 2)

    @staticmethod
    def hash_sha256(text: str, salt: str = "") -> str:
        """Create SHA256 hash from text + salt."""
        return hashlib.sha256((text + salt).encode("utf-8")).hexdigest()


class QuestionPreparer:
    """Main orchestrator for question preparation."""

    _SUPPORTED_SUFFIXES = (".jpg", ".jpeg", ".png", ".webp", ".gif")

    def __init__(self) -> None:
        self.security = SecurityService()
        self.base_dir = Path(__file__).parent
        self.original_data_dir = self.base_dir / "original_data"
        self.source_images_dir = self.original_data_dir / "images"
        self.output_dir = self.base_dir / "data"
        self.images_output_dir = self.base_dir / "assets" / "images"
        self.legacy_zip = self.base_dir / "assets" / "images_archive.zip"

        self.output_dir.mkdir(exist_ok=True)
        self.images_output_dir.mkdir(parents=True, exist_ok=True)

    def validate_input(self) -> bool:
        """Verify required input files and folders exist."""
        input_file = self.original_data_dir / "questions_input.json"

        if not input_file.exists():
            print(f"CHYBA: Soubor neexistuje: {input_file}")
            return False

        if not self.source_images_dir.exists():
            print(f"CHYBA: Adresar neexistuje: {self.source_images_dir}")
            return False

        return True

    def load_input_questions(self) -> List[Dict]:
        """Load authoring questions from JSON."""
        input_file = self.original_data_dir / "questions_input.json"
        try:
            with open(input_file, "r", encoding="utf-8") as file:
                payload = json.load(file)
        except json.JSONDecodeError as exc:
            print(f"CHYBA: Neplatny JSON: {exc}")
            return []

        return payload.get("questions", [])

    def generate_random_image_ids(self, count: int) -> List[str]:
        """Generate random unique image IDs."""
        image_ids = [f"img_{secrets.randbelow(10000):04d}" for _ in range(count)]
        while len(set(image_ids)) != len(image_ids):
            image_ids = [f"img_{secrets.randbelow(10000):04d}" for _ in range(count)]
        return image_ids

    def prepare_questions(self) -> Tuple[List[Dict], Dict[str, str]]:
        """Convert input questions into runtime-safe records and image mapping."""
        input_questions = self.load_input_questions()
        if not input_questions:
            print("CHYBA: Zadane otazky nejsou k dispozici.")
            return [], {}

        image_ids = self.generate_random_image_ids(len(input_questions))
        prepared_questions: List[Dict] = []
        image_mapping: Dict[str, str] = {}

        for index, question in enumerate(input_questions):
            answer = question.get("answer", "").strip()
            image_name = question.get("image", "").strip()

            if not answer or not image_name:
                print(f"WARN: Otazka {index + 1} nema answer/image, preskakuji")
                continue

            normalized_answer = self.security.normalize_text(answer)
            salt = self.security.generate_salt(32)
            answer_hash = self.security.hash_sha256(normalized_answer, salt)

            image_id = image_ids[index]
            image_mapping[image_id] = image_name

            prepared_questions.append(
                {
                    "id": f"q{index + 1:03d}",
                    "category": question.get("category", "general"),
                    "image_id": image_id,
                    "answer_hash": answer_hash,
                    "answer_salt": salt,
                    "answer_length": len(normalized_answer),
                    "difficulty": question.get("difficulty", "medium"),
                    "description": question.get("description", ""),
                }
            )

            print(f"OK: q{index + 1:03d} -> {image_id}")

        return prepared_questions, image_mapping

    def _create_placeholder(self, target_path: Path, label: str) -> None:
        """Create placeholder image when source is missing."""
        image = Image.new("RGB", (960, 540), color="#1e293b")
        draw = ImageDraw.Draw(image)

        for row in range(4):
            for col in range(4):
                x1 = col * 240
                y1 = row * 135
                x2 = x1 + 240
                y2 = y1 + 135
                color = "#334155" if (row + col) % 2 == 0 else "#475569"
                draw.rectangle((x1, y1, x2, y2), fill=color, outline="#64748b", width=2)

        draw.text((30, 25), "Placeholder image", fill="#f8fafc")
        draw.text((30, 60), f"Missing source: {label}", fill="#cbd5e1")
        draw.text((30, 95), "Replace this file with real image", fill="#94a3b8")

        target_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(target_path)

    def _resolve_source_image(self, source_name: str) -> Path:
        """Resolve source image path even if extension differs from input JSON."""
        direct = self.source_images_dir / source_name
        if direct.exists() and direct.suffix.lower() in self._SUPPORTED_SUFFIXES:
            return direct

        stem = Path(source_name).stem
        for path in self.source_images_dir.glob(f"{stem}.*"):
            if path.suffix.lower() in self._SUPPORTED_SUFFIXES:
                return path

        return direct

    def build_images_directory(self, image_mapping: Dict[str, str]) -> bool:
        """Create runtime assets/images content with anonymized names."""
        print("\nPripravuji slozku assets/images...")

        try:
            self.images_output_dir.mkdir(parents=True, exist_ok=True)

            for old_file in self.images_output_dir.iterdir():
                if old_file.is_file() and old_file.suffix.lower() in self._SUPPORTED_SUFFIXES:
                    old_file.unlink()

            for image_id, source_name in image_mapping.items():
                source = self._resolve_source_image(source_name)

                if source.exists() and source.suffix.lower() in self._SUPPORTED_SUFFIXES:
                    suffix = source.suffix.lower()
                    target = self.images_output_dir / f"{image_id}{suffix}"
                    shutil.copy2(source, target)
                    print(f"  OK: {source_name} -> {target.name}")
                    continue

                target = self.images_output_dir / f"{image_id}.png"
                self._create_placeholder(target, source_name)
                print(f"  WARN: {source_name} chybi, vytvoren placeholder {target.name}")

            if self.legacy_zip.exists():
                self.legacy_zip.unlink()
                print("  INFO: odstraneny stary assets/images_archive.zip")

            return True
        except Exception as exc:
            print(f"CHYBA pri priprave obrazku: {exc}")
            return False

    def save_questions_json(self, questions: List[Dict]) -> bool:
        """Write prepared questions to data/questions.json."""
        output_file = self.output_dir / "questions.json"

        try:
            with open(output_file, "w", encoding="utf-8") as file:
                json.dump(
                    {
                        "questions": questions,
                        "prepared_at": datetime.now().isoformat(),
                        "count": len(questions),
                    },
                    file,
                    indent=2,
                    ensure_ascii=False,
                )

            print(f"OK: ulozeno {output_file}")
            return True
        except Exception as exc:
            print(f"CHYBA pri zapisu questions.json: {exc}")
            return False

    def cleanup_originals(self) -> None:
        """Optional cleanup of original source image files."""
        response = input(
            "\nSmazat original_data/images obsah? (zadejte 'ano' pro potvrzeni): "
        ).strip().lower()

        if response != "ano":
            print("INFO: Originalni obrazky zustaly beze zmen.")
            return

        try:
            if self.source_images_dir.exists():
                shutil.rmtree(self.source_images_dir)
            self.source_images_dir.mkdir(parents=True, exist_ok=True)
            print("OK: Originalni obrazky byly smazany.")
        except Exception as exc:
            print(f"WARN: Mazani selhalo: {exc}")

    def run(self) -> bool:
        """Run full preparation workflow."""
        print("=" * 68)
        print("PRIPRAVA QUIZ DAT")
        print("=" * 68)

        print("\n1) Validace vstupu")
        if not self.validate_input():
            return False
        print("OK")

        print("\n2) Hashovani a priprava otazek")
        questions, image_mapping = self.prepare_questions()
        if not questions:
            return False

        print("\n3) Kopirovani obrazku do assets/images")
        if not self.build_images_directory(image_mapping):
            return False

        print("\n4) Ulozeni data/questions.json")
        if not self.save_questions_json(questions):
            return False

        print("\n5) Volitelny cleanup original_data/images")
        self.cleanup_originals()

        print("\n" + "=" * 68)
        print("HOTOVO")
        print("=" * 68)
        print(
            """
Vystupy:
  - data/questions.json
  - assets/images/<image_id>.jpg|png|...

Bezpecnost:
  - Odpovedi jsou ulozene pouze jako hash + salt
  - Nazvy runtime obrazku jsou anonymni (img_XXXX)
"""
        )
        return True


def main() -> None:
    """CLI entry point."""
    preparer = QuestionPreparer()
    ok = preparer.run()
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
