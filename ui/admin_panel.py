"""Panel správce pro výběr otázek a spuštění kola bez odhalení odpovědí."""

import json
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Callable, Dict, List, Optional, Tuple
import logging
import sys
from pathlib import Path

# Ensure root directory is in path for imports
_root_dir = str(Path(__file__).parent.parent)
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)

from ui.components import ModernButton
from ui.theme import COLORS, FONTS
from services.question_loader import QuestionLoader
from services.image_upload_service import ImageUploadService
from services.admin_question_manager import AdminQuestionManager
from models.question import Question
from config import CONFIG


logger = logging.getLogger(__name__)


class AdminPanel(tk.Frame):
    """Admin panel pro výběr otázky a spuštění kola."""
    
    def __init__(self, parent, on_start_round: Callable = None, on_back: Callable = None, **kwargs):
        """Inicializuje admin panel."""
        super().__init__(parent, bg=COLORS["bg_primary"], **kwargs)
        
        self.on_start_round = on_start_round
        self.on_back = on_back
        self.loader: Optional[QuestionLoader] = None
        self.all_questions = []
        self.selected_question: Optional[Question] = None
        self.question_manager = AdminQuestionManager(CONFIG.questions_json)
        self.image_upload_service = ImageUploadService()
        self.project_root = Path(_root_dir)

        self._load_questions_safe()
        
        self._build_ui()
        logger.info(f"AdminPanel initialized with {len(self.all_questions)} questions")

    def _load_questions_safe(self) -> None:
        """Load runtime questions; fallback to empty list if file is empty/invalid."""
        try:
            self.loader = QuestionLoader(CONFIG.questions_json)
            self.all_questions = self.loader.load_all()
        except Exception as exc:
            self.loader = None
            self.all_questions = []
            logger.warning(
                "Questions could not be loaded; admin panel continues without questions: %s",
                exc,
            )
    
    def _build_ui(self) -> None:
        """Vytvoří rozložení panelu."""
        # Top: Title
        title_frame = tk.Frame(self, bg=COLORS["bg_secondary"], height=60)
        title_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(
            title_frame,
            text="Výběr otázky",
            font=FONTS["title"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_primary"]
        ).pack(pady=10)
        
        # Filters
        self._build_filters(title_frame)
        
        # Main content: Left (list) + Right (preview)
        main_frame = tk.Frame(self, bg=COLORS["bg_primary"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self._build_question_list(main_frame)
        self._build_preview(main_frame)
        
        # Bottom: Action buttons
        self._build_bottom(self)
    
    def _build_filters(self, parent) -> None:
        """Vytvoří ovládací prvky filtrů."""
        filter_frame = tk.Frame(parent, bg=COLORS["bg_secondary"])
        filter_frame.pack(fill=tk.X, pady=10)

        # Category filter
        tk.Label(
            filter_frame,
            text="Kategorie:",
            font=FONTS["body"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["accent"]  # Use accent color for better visibility
        ).pack(side=tk.LEFT, padx=5)

        categories = ["Vše"] + list(set(q.category for q in self.all_questions))
        self.category_var = tk.StringVar(value="Vše")
        self.category_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.category_var,
            values=categories,
            state="readonly",
            width=15
        )
        self.category_combo.pack(side=tk.LEFT, padx=5)
        self.category_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_list())

        # Difficulty filter
        tk.Label(
            filter_frame,
            text="Obtížnost:",
            font=FONTS["body"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["accent"]  # Use accent color for better visibility
        ).pack(side=tk.LEFT, padx=5)

        difficulties = ["Vše"] + list(set(q.difficulty for q in self.all_questions))
        self.difficulty_var = tk.StringVar(value="Vše")
        self.difficulty_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.difficulty_var,
            values=difficulties,
            state="readonly",
            width=15
        )
        self.difficulty_combo.pack(side=tk.LEFT, padx=5)
        self.difficulty_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_list())

        self._refresh_filter_options()
    
    def _build_question_list(self, parent) -> None:
        """Vytvoří seznam otázek."""
        list_frame = tk.Frame(parent, bg=COLORS["bg_secondary"])
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        tk.Label(
            list_frame,
            text="Otázky",
            font=FONTS["heading"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_primary"]
        ).pack(pady=10)
        
        # Scrollbar + table with mini edit action in each row
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.question_tree = ttk.Treeview(
            list_frame,
            columns=("question", "edit"),
            show="headings",
            height=15,
            yscrollcommand=scrollbar.set,
        )
        self.question_tree.heading("question", text="Otázka")
        self.question_tree.heading("edit", text="")
        self.question_tree.column("question", width=360, anchor=tk.W)
        self.question_tree.column("edit", width=50, anchor=tk.CENTER)
        self.question_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.question_tree.bind("<<TreeviewSelect>>", self._on_question_select)
        self.question_tree.bind("<Button-1>", self._on_question_tree_click)
        scrollbar.config(command=self.question_tree.yview)
        
        # Populate list
        self._refresh_list()
    
    def _build_preview(self, parent) -> None:
        """Vytvoří panel náhledu vybrané otázky."""
        preview_frame = tk.Frame(parent, bg=COLORS["bg_secondary"])
        preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=10)
        
        tk.Label(
            preview_frame,
            text="Náhled",
            font=FONTS["heading"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_primary"]
        ).pack(pady=10)
        
        # Info frame
        info_frame = tk.Frame(preview_frame, bg=COLORS["bg_tertiary"])
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ID
        tk.Label(
            info_frame,
            text="ID:",
            font=FONTS["body"],
            bg=COLORS["bg_tertiary"],
            fg=COLORS["fg_secondary"]
        ).pack(anchor=tk.W, padx=5, pady=2)
        
        self.preview_id = tk.Label(
            info_frame,
            text="-",
            font=FONTS["mono"],
            bg=COLORS["bg_tertiary"],
            fg=COLORS["fg_primary"]
        )
        self.preview_id.pack(anchor=tk.W, padx=10)
        
        # Category
        tk.Label(
            info_frame,
            text="Kategorie:",
            font=FONTS["body"],
            bg=COLORS["bg_tertiary"],
            fg=COLORS["fg_secondary"]
        ).pack(anchor=tk.W, padx=5, pady=2)
        
        self.preview_category = tk.Label(
            info_frame,
            text="-",
            font=FONTS["mono"],
            bg=COLORS["bg_tertiary"],
            fg=COLORS["fg_primary"]
        )
        self.preview_category.pack(anchor=tk.W, padx=10)
        
        # Difficulty
        tk.Label(
            info_frame,
            text="Obtížnost:",
            font=FONTS["body"],
            bg=COLORS["bg_tertiary"],
            fg=COLORS["fg_secondary"]
        ).pack(anchor=tk.W, padx=5, pady=2)
        
        self.preview_difficulty = tk.Label(
            info_frame,
            text="-",
            font=FONTS["mono"],
            bg=COLORS["bg_tertiary"],
            fg=COLORS["fg_primary"]
        )
        self.preview_difficulty.pack(anchor=tk.W, padx=10)
        
        # Answer length
        tk.Label(
            info_frame,
            text="Délka odpovědi:",
            font=FONTS["body"],
            bg=COLORS["bg_tertiary"],
            fg=COLORS["fg_secondary"]
        ).pack(anchor=tk.W, padx=5, pady=2)
        
        self.preview_length = tk.Label(
            info_frame,
            text="-",
            font=FONTS["mono"],
            bg=COLORS["bg_tertiary"],
            fg=COLORS["fg_primary"]
        )
        self.preview_length.pack(anchor=tk.W, padx=10)
        
        # Note
        tk.Label(
            preview_frame,
            text="⚠ Odpověď se z bezpečnostních důvodů\nnikdy nezobrazí",
            font=FONTS["small"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["warning"],
            justify=tk.CENTER
        ).pack(pady=10)
    
    def _build_bottom(self, parent) -> None:
        """Vytvoří spodní akční tlačítka."""
        button_frame = tk.Frame(parent, bg=COLORS["bg_primary"])
        button_frame.pack(fill=tk.X, padx=20, pady=20)

        ModernButton(
            button_frame,
            "Vytvořit otázku",
            command=self._handle_create_question,
            bg_color=COLORS["accent"],
            width=20,
            height=2
        ).pack(side=tk.LEFT, padx=10)

        ModernButton(
            button_frame,
            "Spustit kolo",
            command=self._handle_start_round,
            bg_color=COLORS["success"],
            width=20,
            height=2
        ).pack(side=tk.LEFT, padx=10)
        
        ModernButton(
            button_frame,
            "Zpět na hlavní menu",
            command=self._handle_back,
            bg_color=COLORS["accent"],
            width=20,
            height=2
        ).pack(side=tk.LEFT, padx=10)
        
        ModernButton(
            button_frame,
            "Konec",
            command=self._handle_quit,
            bg_color=COLORS["danger"],
            width=20,
            height=2
        ).pack(side=tk.LEFT, padx=10)

    def _handle_start_round(self) -> None:
        """Spustí kolo s vybranou otázkou."""
        if not self.selected_question:
            messagebox.showwarning("Chyba", "Prosím vyberte nejdříve otázku")
            return

        if self.on_start_round:
            logger.info(f"Starting round from admin panel: {self.selected_question.id}")
            self.on_start_round(self.selected_question)
        else:
            logger.warning("Callback on_start_round není nastaven")
    
    def _refresh_list(self) -> None:
        """Obnoví seznam otázek podle filtrů."""
        category = self.category_var.get()
        difficulty = self.difficulty_var.get()
        
        # Filter questions
        filtered = self.all_questions
        
        if category != "Vše":
            filtered = [q for q in filtered if q.category == category]
        
        if difficulty != "Vše":
            filtered = [q for q in filtered if q.difficulty == difficulty]
        
        # Update table
        for item_id in self.question_tree.get_children():
            self.question_tree.delete(item_id)

        for q in filtered:
            row_text = f"{q.id} | {q.category} ({q.difficulty})"
            self.question_tree.insert(
                "",
                tk.END,
                iid=q.id,
                values=(row_text, "✎"),
            )
        
        logger.info(f"Filtered to {len(filtered)} questions")

    def _refresh_filter_options(self) -> None:
        """Obnoví hodnoty comboboxů podle aktuálních otázek."""
        categories = ["Vše"] + sorted({q.category for q in self.all_questions})
        difficulties = ["Vše"] + sorted({q.difficulty for q in self.all_questions})

        self.category_combo["values"] = categories
        self.difficulty_combo["values"] = difficulties

        if self.category_var.get() not in categories:
            self.category_var.set("Vše")
        if self.difficulty_var.get() not in difficulties:
            self.difficulty_var.set("Vše")
    
    def _on_question_select(self, event) -> None:
        """Zpracuje výběr otázky v seznamu."""
        if not self.loader:
            self.selected_question = None
            return

        selection = self.question_tree.selection()
        if not selection:
            return

        question_id = selection[0]
        
        # Find question
        self.selected_question = self.loader.get_by_id(question_id)
        
        if self.selected_question:
            # Update preview
            self.preview_id.config(text=self.selected_question.id)
            self.preview_category.config(text=self.selected_question.category)
            self.preview_difficulty.config(text=self.selected_question.difficulty)
            self.preview_length.config(text=str(self.selected_question.answer_length))
            
            logger.info(f"Question selected: {question_id}")

    def _on_question_tree_click(self, event) -> Optional[str]:
        """Handle row-level click; edit icon opens editor for that question."""
        region = self.question_tree.identify("region", event.x, event.y)
        if region != "cell":
            return None

        column = self.question_tree.identify_column(event.x)
        row_id = self.question_tree.identify_row(event.y)

        if not row_id:
            return None

        if column == "#2":
            self._open_runtime_question_editor(row_id)
            return "break"

        return None

    def _open_runtime_question_editor(self, question_id: str) -> None:
        """Open compact editor for one runtime question from data/questions.json."""
        question = self.question_manager.get_question(question_id)
        if not question:
            messagebox.showerror("Chyba", f"Otázka {question_id} nebyla nalezena")
            return

        dialog = tk.Toplevel(self)
        dialog.title(f"Upravit {question_id}")
        dialog.configure(bg=COLORS["bg_secondary"])
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        container = tk.Frame(dialog, bg=COLORS["bg_secondary"])
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(
            container,
            text=f"Úprava otázky {question_id}",
            font=FONTS["heading"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_primary"],
        ).pack(anchor=tk.W, pady=(0, 10))

        category_var = tk.StringVar(value=str(question.get("category", "general")))
        difficulty_var = tk.StringVar(value=str(question.get("difficulty", "medium")))
        description_var = tk.StringVar(value=str(question.get("description", "")))
        image_var = tk.StringVar(value=str(question.get("image_id", "")))
        answer_var = tk.StringVar()

        self._create_form_row(container, "Kategorie:", category_var)

        diff_row = tk.Frame(container, bg=COLORS["bg_secondary"])
        diff_row.pack(fill=tk.X, pady=6)
        tk.Label(
            diff_row,
            text="Obtížnost:",
            width=20,
            anchor=tk.W,
            font=FONTS["body"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_primary"],
        ).pack(side=tk.LEFT)
        ttk.Combobox(
            diff_row,
            textvariable=difficulty_var,
            values=["easy", "medium", "hard"],
            state="readonly",
            width=27,
        ).pack(side=tk.LEFT)

        self._create_form_row(container, "Popis:", description_var)
        self._create_form_row(container, "Obrázek (ID/cesta):", image_var)
        self._create_form_row(container, "Nová správná odpověď:", answer_var)

        tk.Label(
            container,
            text="Odpověď je volitelná. Vyplňte ji jen pokud chcete změnit hash odpovědi.",
            font=FONTS["small"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_secondary"],
            justify=tk.LEFT,
        ).pack(anchor=tk.W, pady=(2, 0))

        button_row = tk.Frame(container, bg=COLORS["bg_secondary"])
        button_row.pack(fill=tk.X, pady=(16, 0))

        ModernButton(
            button_row,
            "Uložit",
            command=lambda: self._save_runtime_question_update(
                dialog,
                question_id=question_id,
                current_image_id=str(question.get("image_id", "")),
                category=category_var.get(),
                difficulty=difficulty_var.get(),
                description=description_var.get(),
                image_input=image_var.get(),
                new_answer=answer_var.get(),
            ),
            bg_color=COLORS["success"],
            width=14,
            height=1,
        ).pack(side=tk.LEFT, padx=(0, 8))

        ModernButton(
            button_row,
            "Zavřít",
            command=dialog.destroy,
            bg_color=COLORS["danger"],
            width=12,
            height=1,
        ).pack(side=tk.LEFT)

    def _save_runtime_question_update(
        self,
        dialog: tk.Toplevel,
        question_id: str,
        current_image_id: str,
        category: str,
        difficulty: str,
        description: str,
        image_input: str,
        new_answer: str,
    ) -> None:
        """Persist one runtime question update; answer is hashed automatically."""
        category = category.strip()
        difficulty = difficulty.strip()
        description = description.strip()
        image_input = image_input.strip()
        new_answer = new_answer.strip()

        if not category:
            messagebox.showwarning("Chyba", "Zadejte kategorii")
            return
        if difficulty not in {"easy", "medium", "hard"}:
            messagebox.showwarning("Chyba", "Obtížnost musí být easy, medium nebo hard")
            return
        if not image_input:
            messagebox.showwarning("Chyba", "Zadejte image_id nebo cestu k obrázku")
            return

        try:
            image_id = self._resolve_runtime_image_id(image_input, current_image_id=current_image_id)

            updates = {
                "category": category,
                "difficulty": difficulty,
                "description": description,
                "image_id": image_id,
            }
            answer_changed = bool(new_answer)
            if new_answer:
                updates["answer"] = new_answer

            self.question_manager.update_question(question_id, updates)
            self._reload_runtime_questions()
            self._select_question_in_list(question_id)
            if answer_changed:
                messagebox.showinfo("Hotovo", "Otázka byla upravena a odpověď byla zahashována.")
            else:
                messagebox.showinfo("Hotovo", "Otázka byla upravena.")
            dialog.destroy()
        except Exception as exc:
            logger.error(f"Runtime question update failed: {exc}")
            messagebox.showerror("Chyba", f"Uložení se nezdařilo: {exc}")

    def _select_question_in_list(self, question_id: str) -> None:
        """Select question row by id and refresh preview."""
        if not hasattr(self, "question_tree"):
            return
        if not self.question_tree.exists(question_id):
            return

        self.question_tree.selection_set(question_id)
        self.question_tree.focus(question_id)
        self._on_question_select(None)
    
    def _handle_create_question(self) -> None:
        """Otevře formulář pro přidání nové otázky do data/questions.json."""
        dialog = tk.Toplevel(self)
        dialog.title("Vytvořit otázku")
        dialog.configure(bg=COLORS["bg_secondary"])
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        container = tk.Frame(dialog, bg=COLORS["bg_secondary"])
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(
            container,
            text="Nová otázka (uložení přímo do data/questions.json)",
            font=FONTS["heading"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_primary"]
        ).pack(anchor=tk.W, pady=(0, 10))

        answer_var = tk.StringVar()
        image_var = tk.StringVar()
        category_var = tk.StringVar(value="general")
        difficulty_var = tk.StringVar(value="medium")
        description_var = tk.StringVar()

        self._create_form_row(container, "Správná odpověď:", answer_var)
        self._create_form_row(container, "Kategorie:", category_var)

        diff_row = tk.Frame(container, bg=COLORS["bg_secondary"])
        diff_row.pack(fill=tk.X, pady=6)
        tk.Label(
            diff_row,
            text="Obtížnost:",
            width=20,
            anchor=tk.W,
            font=FONTS["body"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_primary"]
        ).pack(side=tk.LEFT)
        ttk.Combobox(
            diff_row,
            textvariable=difficulty_var,
            values=["easy", "medium", "hard"],
            state="readonly",
            width=27
        ).pack(side=tk.LEFT)

        self._create_form_row(container, "Popis (volitelné):", description_var)

        image_row = tk.Frame(container, bg=COLORS["bg_secondary"])
        image_row.pack(fill=tk.X, pady=6)
        tk.Label(
            image_row,
            text="Obrázek:",
            width=20,
            anchor=tk.W,
            font=FONTS["body"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_primary"]
        ).pack(side=tk.LEFT)

        image_entry = tk.Entry(
            image_row,
            textvariable=image_var,
            width=30,
            font=FONTS["body"],
            bg=COLORS["bg_tertiary"],
            fg=COLORS["fg_primary"],
            relief=tk.FLAT
        )
        image_entry.pack(side=tk.LEFT, padx=(0, 8))

        ModernButton(
            image_row,
            "Vybrat",
            command=lambda: self._pick_source_image(image_var),
            bg_color=COLORS["accent"],
            width=10,
            height=1
        ).pack(side=tk.LEFT)

        tk.Label(
            container,
            text="Poznámka: Obrázky pro otázky musí být v cestě original_data/images.",
            font=FONTS["small"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_secondary"],
            justify=tk.LEFT,
        ).pack(anchor=tk.W, pady=(2, 0))

        button_row = tk.Frame(container, bg=COLORS["bg_secondary"])
        button_row.pack(fill=tk.X, pady=(16, 0))

        ModernButton(
            button_row,
            "Uložit otázku",
            command=lambda: self._save_new_runtime_question(
                dialog,
                answer=answer_var.get(),
                category=category_var.get(),
                difficulty=difficulty_var.get(),
                description=description_var.get(),
                source_image=image_var.get(),
            ),
            bg_color=COLORS["success"],
            width=18,
            height=1
        ).pack(side=tk.LEFT, padx=(0, 8))

        ModernButton(
            button_row,
            "Zavřít",
            command=dialog.destroy,
            bg_color=COLORS["danger"],
            width=12,
            height=1
        ).pack(side=tk.LEFT)

    def _create_form_row(self, parent: tk.Widget, label: str, variable: tk.StringVar) -> None:
        """Vytvoří řádek formuláře s popiskem a vstupem."""
        row = tk.Frame(parent, bg=COLORS["bg_secondary"])
        row.pack(fill=tk.X, pady=6)
        tk.Label(
            row,
            text=label,
            width=20,
            anchor=tk.W,
            font=FONTS["body"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_primary"]
        ).pack(side=tk.LEFT)
        tk.Entry(
            row,
            textvariable=variable,
            width=40,
            font=FONTS["body"],
            bg=COLORS["bg_tertiary"],
            fg=COLORS["fg_primary"],
            relief=tk.FLAT
        ).pack(side=tk.LEFT)

    def _pick_source_image(self, image_var: tk.StringVar) -> None:
        """Vybere lokální obrázek pro novou otázku."""
        target_dir = self.project_root / "original_data" / "images"
        file_path = filedialog.askopenfilename(
            title="Vyberte obrázek pro novou otázku",
            initialdir=str(target_dir),
            filetypes=[
                ("Obrázky", "*.jpg *.jpeg *.png *.gif *.webp"),
                ("Všechny soubory", "*.*"),
            ],
        )
        if file_path:
            image_var.set(file_path)

    def _save_new_runtime_question(
        self,
        dialog: tk.Toplevel,
        answer: str,
        category: str,
        difficulty: str,
        description: str,
        source_image: str,
    ) -> None:
        """Create runtime question in data/questions.json with immediate hashing."""
        answer = answer.strip()
        category = category.strip()
        difficulty = difficulty.strip()
        description = description.strip()
        source_image = source_image.strip()

        if not answer:
            messagebox.showwarning("Chyba", "Zadejte správnou odpověď")
            return
        if not source_image:
            messagebox.showwarning("Chyba", "Vyberte obrázek")
            return
        if not category:
            messagebox.showwarning("Chyba", "Zadejte kategorii")
            return
        if difficulty not in {"easy", "medium", "hard"}:
            messagebox.showwarning("Chyba", "Obtížnost musí být easy, medium nebo hard")
            return

        try:
            image_id = self._resolve_runtime_image_id(source_image)
            created = self.question_manager.create_question(
                answer=answer,
                category=category,
                difficulty=difficulty,
                description=description,
                image_id=image_id,
            )
            self._reload_runtime_questions()
            self._select_question_in_list(created["id"])
            messagebox.showinfo(
                "Hotovo",
                f"Otázka {created['id']} byla vytvořena a automaticky zahashována."
            )
            logger.info("New runtime question created in data/questions.json")
            dialog.destroy()
        except Exception as exc:
            logger.error(f"Failed to create runtime question: {exc}")
            messagebox.showerror("Chyba", f"Otázku se nepodařilo uložit: {exc}")

    def _handle_edit_input_questions(self) -> None:
        """Open dialog for editing existing questions in original_data/questions_input.json."""
        payload, questions = self._load_input_questions_payload()
        if not questions:
            messagebox.showinfo(
                "Bez otázek",
                "Ve vstupním souboru original_data/questions_input.json zatím nejsou žádné otázky."
            )
            return

        dialog = tk.Toplevel(self)
        dialog.title("Upravit existující otázky")
        dialog.configure(bg=COLORS["bg_secondary"])
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        container = tk.Frame(dialog, bg=COLORS["bg_secondary"])
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(
            container,
            text="Úprava otázek (original_data/questions_input.json)",
            font=FONTS["heading"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_primary"],
        ).pack(anchor=tk.W, pady=(0, 10))

        selector_row = tk.Frame(container, bg=COLORS["bg_secondary"])
        selector_row.pack(fill=tk.X, pady=6)

        tk.Label(
            selector_row,
            text="Otázka:",
            width=20,
            anchor=tk.W,
            font=FONTS["body"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_primary"],
        ).pack(side=tk.LEFT)

        question_selector = ttk.Combobox(
            selector_row,
            state="readonly",
            width=50,
        )
        question_selector.pack(side=tk.LEFT)

        answer_var = tk.StringVar()
        image_var = tk.StringVar()
        category_var = tk.StringVar()
        difficulty_var = tk.StringVar(value="medium")
        description_var = tk.StringVar()

        self._create_form_row(container, "Správná odpověď:", answer_var)
        self._create_form_row(container, "Kategorie:", category_var)

        diff_row = tk.Frame(container, bg=COLORS["bg_secondary"])
        diff_row.pack(fill=tk.X, pady=6)
        tk.Label(
            diff_row,
            text="Obtížnost:",
            width=20,
            anchor=tk.W,
            font=FONTS["body"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_primary"],
        ).pack(side=tk.LEFT)
        ttk.Combobox(
            diff_row,
            textvariable=difficulty_var,
            values=["easy", "medium", "hard"],
            state="readonly",
            width=27,
        ).pack(side=tk.LEFT)

        self._create_form_row(container, "Popis (volitelné):", description_var)

        image_row = tk.Frame(container, bg=COLORS["bg_secondary"])
        image_row.pack(fill=tk.X, pady=6)
        tk.Label(
            image_row,
            text="Obrázek:",
            width=20,
            anchor=tk.W,
            font=FONTS["body"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_primary"],
        ).pack(side=tk.LEFT)

        tk.Entry(
            image_row,
            textvariable=image_var,
            width=30,
            font=FONTS["body"],
            bg=COLORS["bg_tertiary"],
            fg=COLORS["fg_primary"],
            relief=tk.FLAT,
        ).pack(side=tk.LEFT, padx=(0, 8))

        ModernButton(
            image_row,
            "Vybrat",
            command=lambda: self._pick_source_image(image_var),
            bg_color=COLORS["accent"],
            width=10,
            height=1,
        ).pack(side=tk.LEFT)

        tk.Label(
            container,
            text="Poznámka: Obrázky pro otázky musí být v cestě original_data/images.",
            font=FONTS["small"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_secondary"],
            justify=tk.LEFT,
        ).pack(anchor=tk.W, pady=(2, 0))

        def load_selected_question(_event=None) -> None:
            idx = question_selector.current()
            if idx < 0 or idx >= len(questions):
                return

            question = questions[idx]
            answer_var.set(str(question.get("answer", "")))
            image_var.set(str(question.get("image", "")))
            category_var.set(str(question.get("category", "general")))
            difficulty_var.set(str(question.get("difficulty", "medium")))
            description_var.set(str(question.get("description", "")))

        def save_selected_question() -> None:
            idx = question_selector.current()
            if idx < 0 or idx >= len(questions):
                messagebox.showwarning("Chyba", "Nejprve vyberte otázku")
                return

            answer = answer_var.get().strip()
            image = image_var.get().strip()
            category = category_var.get().strip()
            difficulty = difficulty_var.get().strip()
            description = description_var.get().strip()

            if not answer:
                messagebox.showwarning("Chyba", "Zadejte správnou odpověď")
                return
            if not image:
                messagebox.showwarning("Chyba", "Vyberte obrázek")
                return
            if not category:
                messagebox.showwarning("Chyba", "Zadejte kategorii")
                return
            if difficulty not in {"easy", "medium", "hard"}:
                messagebox.showwarning("Chyba", "Obtížnost musí být easy, medium nebo hard")
                return

            try:
                image_name = self._resolve_image_from_original_data(image)
            except Exception as exc:
                messagebox.showerror("Chyba", str(exc))
                return

            question = questions[idx]
            question["answer"] = answer
            question["image"] = image_name
            question["category"] = category
            question["difficulty"] = difficulty
            question["description"] = description

            self._save_input_questions_payload(payload)
            refresh_selector(idx)
            messagebox.showinfo("Hotovo", "Otázka byla upravena.")

        def delete_selected_question() -> None:
            idx = question_selector.current()
            if idx < 0 or idx >= len(questions):
                messagebox.showwarning("Chyba", "Nejprve vyberte otázku")
                return

            if not messagebox.askyesno("Potvrzení", "Opravdu chcete tuto otázku smazat?"):
                return

            del questions[idx]
            self._save_input_questions_payload(payload)

            if not questions:
                messagebox.showinfo(
                    "Hotovo",
                    "Otázka byla smazána. Ve vstupním souboru již nejsou žádné otázky."
                )
                dialog.destroy()
                return

            refresh_selector(max(0, idx - 1))
            messagebox.showinfo("Hotovo", "Otázka byla smazána.")

        def refresh_selector(select_index: int = 0) -> None:
            values = [self._format_input_question_label(i, q) for i, q in enumerate(questions)]
            question_selector["values"] = values
            if not values:
                return

            safe_index = min(max(select_index, 0), len(values) - 1)
            question_selector.current(safe_index)
            load_selected_question()

        question_selector.bind("<<ComboboxSelected>>", load_selected_question)
        refresh_selector()

        button_row = tk.Frame(container, bg=COLORS["bg_secondary"])
        button_row.pack(fill=tk.X, pady=(16, 0))

        ModernButton(
            button_row,
            "Uložit změny",
            command=save_selected_question,
            bg_color=COLORS["success"],
            width=18,
            height=1,
        ).pack(side=tk.LEFT, padx=(0, 8))

        ModernButton(
            button_row,
            "Smazat otázku",
            command=delete_selected_question,
            bg_color=COLORS["danger"],
            width=16,
            height=1,
        ).pack(side=tk.LEFT, padx=(0, 8))

        ModernButton(
            button_row,
            "Zavřít",
            command=dialog.destroy,
            bg_color=COLORS["danger"],
            width=12,
            height=1,
        ).pack(side=tk.LEFT)

    def _resolve_image_from_original_data(self, source_image: str) -> str:
        """Validate image path and ensure it points into original_data/images."""
        target_dir = (self.project_root / "original_data" / "images").resolve()
        target_dir.mkdir(parents=True, exist_ok=True)

        source_path = Path(source_image)
        candidates = []
        if source_path.is_absolute():
            candidates.append(source_path)
        else:
            candidates.append(self.project_root / source_path)
            candidates.append(target_dir / source_path.name)

        resolved_path = None
        for candidate in candidates:
            try:
                candidate_resolved = candidate.resolve()
            except Exception:
                continue
            if candidate_resolved.exists() and candidate_resolved.is_file():
                resolved_path = candidate_resolved
                break

        if resolved_path is None:
            raise FileNotFoundError(
                "Neplatná cesta k obrázku. Zkontrolujte, že soubor existuje a je v originální složce obrázků. "
                "Správný formát cesty je například: ./original_data/images/img_001.png"
            )

        try:
            resolved_path.relative_to(target_dir)
        except ValueError as exc:
            raise ValueError(
                "Neplatná cesta k obrázku. Obrázek musí být umístěný ve složce original_data/images. "
                "Správný formát cesty je například: ./original_data/images/img_001.png"
            ) from exc

        suffix = resolved_path.suffix.lower()
        allowed = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
        if suffix not in allowed:
            raise ValueError("Nepodporovaný formát obrázku")

        return resolved_path.name

    def _resolve_runtime_image_id(
        self,
        image_input: str,
        current_image_id: Optional[str] = None,
    ) -> str:
        """Resolve runtime image id from existing id or upload from original_data/images path."""
        image_input = image_input.strip()
        if not image_input:
            raise ValueError("Zadejte image_id nebo cestu k obrázku")

        if current_image_id and image_input == current_image_id:
            return current_image_id

        if self._runtime_image_exists(image_input):
            return image_input

        image_name = self._resolve_image_from_original_data(image_input)
        source_path = self.project_root / "original_data" / "images" / image_name
        upload_result = self.image_upload_service.upload_image(
            file_path=str(source_path),
            reference_name=image_name,
        )

        if not upload_result.get("success"):
            error_msg = upload_result.get("error", "Neznámá chyba")
            raise ValueError(f"Nahrání obrázku selhalo: {error_msg}")

        return str(upload_result.get("image_id"))

    def _runtime_image_exists(self, image_id: str) -> bool:
        """Check whether runtime image_id exists in assets/images."""
        image_id = image_id.strip()
        if not image_id:
            return False

        images_dir = self.project_root / "assets" / "images"
        if not images_dir.exists():
            return False

        return any(path.is_file() for path in images_dir.glob(f"{image_id}.*"))

    def _append_question_to_input_json(
        self,
        answer: str,
        image_name: str,
        category: str,
        difficulty: str,
        description: str,
    ) -> None:
        """Přidá otázku do original_data/questions_input.json."""
        payload, questions = self._load_input_questions_payload()

        questions.append(
            {
                "answer": answer,
                "image": image_name,
                "category": category,
                "difficulty": difficulty,
                "description": description,
            }
        )

        self._save_input_questions_payload(payload)

    def _load_input_questions_payload(self) -> Tuple[Dict, List]:
        """Load questions_input payload and return mutable (payload, questions) pair."""
        input_path = self.project_root / "original_data" / "questions_input.json"
        payload = {}

        if input_path.exists():
            with open(input_path, "r", encoding="utf-8") as file:
                payload = json.load(file)

        if not isinstance(payload, dict):
            payload = {}

        questions = payload.get("questions")
        if not isinstance(questions, list):
            questions = []
            payload["questions"] = questions

        return payload, questions

    def _save_input_questions_payload(self, payload: dict) -> None:
        """Persist payload to original_data/questions_input.json."""
        input_path = self.project_root / "original_data" / "questions_input.json"
        with open(input_path, "w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2, ensure_ascii=False)

    @staticmethod
    def _format_input_question_label(index: int, question: dict) -> str:
        """Format user-friendly selector label for editable input question."""
        category = str(question.get("category", "general"))
        difficulty = str(question.get("difficulty", "medium"))
        image = str(question.get("image", "-"))
        answer = str(question.get("answer", ""))
        preview = (answer[:24] + "...") if len(answer) > 24 else answer
        return f"{index + 1}. {category}/{difficulty} | {image} | {preview}"

    def _handle_hash_new_questions(self) -> None:
        """Spustí app/quiz_app.py pro zahashování a přípravu nových otázek."""
        confirm = messagebox.askyesno(
            "Potvrzení",
            "Spustit hashování nových otázek?\n"
            "Po dokončení se questions v original_data/questions_input.json vyprázdní."
        )
        if not confirm:
            return

        quiz_app_path = self.project_root / "app" / "quiz_app.py"
        if not quiz_app_path.exists():
            messagebox.showerror("Chyba", "Soubor app/quiz_app.py nebyl nalezen")
            return

        try:
            result = subprocess.run(
                [sys.executable, str(quiz_app_path)],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                check=False,
            )
        except Exception as exc:
            logger.error(f"Failed to run quiz_app.py: {exc}")
            messagebox.showerror("Chyba", f"Nepodařilo se spustit quiz_app.py: {exc}")
            return

        if result.returncode != 0:
            output = (result.stderr or result.stdout or "Neznámá chyba").strip()
            trimmed_output = output[-1000:] if len(output) > 1000 else output
            messagebox.showerror(
                "Chyba",
                "Hashování selhalo.\n\n"
                f"Výstup:\n{trimmed_output}"
            )
            logger.error(f"quiz_app.py failed with code {result.returncode}: {trimmed_output}")
            return

        self._reload_runtime_questions()
        messagebox.showinfo(
            "Hotovo",
            "Otázky byly zahashovány a data/questions.json byla aktualizována.\n"
            "Vstupní seznam otázek byl vyčištěn."
        )

    def _reload_runtime_questions(self) -> None:
        """Znovu načte runtime otázky po hashování."""
        self.question_manager = AdminQuestionManager(CONFIG.questions_json)
        self._load_questions_safe()
        self.selected_question = None

        self.preview_id.config(text="-")
        self.preview_category.config(text="-")
        self.preview_difficulty.config(text="-")
        self.preview_length.config(text="-")

        self._refresh_filter_options()
        self._refresh_list()
    
    def _handle_back(self) -> None:
        """Vrátí uživatele na hlavní menu."""
        logger.info("Návrat na hlavní menu")
        
        if self.on_back:
            self.on_back()
    
    def _handle_quit(self) -> None:
        """Ukončí aplikaci z admin panelu."""
        if messagebox.askyesno("Konec", "Chcete opustit aplikaci?"):
            self.master.quit()


if __name__ == "__main__":
    print("Komponenta AdminPanel - použití viz main.py")
