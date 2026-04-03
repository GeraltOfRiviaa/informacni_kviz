"""Panel správce pro výběr otázek a spuštění kola bez odhalení odpovědí."""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Callable, Optional
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
        self.loader = QuestionLoader(CONFIG.questions_json)
        self.all_questions = self.loader.load_all()
        self.selected_question: Optional[Question] = None
        self.image_upload_service = ImageUploadService()
        
        self._build_ui()
        logger.info(f"AdminPanel initialized with {len(self.all_questions)} questions")
    
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
        
        # Scrollbar + Listbox
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.question_listbox = tk.Listbox(
            list_frame,
            bg=COLORS["bg_tertiary"],
            fg=COLORS["fg_primary"],
            selectmode=tk.SINGLE,
            yscrollcommand=scrollbar.set,
            font=FONTS["body"],
            height=15,
            width=40
        )
        self.question_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.question_listbox.bind("<<ListboxSelect>>", self._on_question_select)
        scrollbar.config(command=self.question_listbox.yview)
        
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
        
        # Upload image button
        tk.Label(
            preview_frame,
            text="Obrázek:",
            font=FONTS["body"],
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg_primary"]
        ).pack(pady=(20, 5))
        
        ModernButton(
            preview_frame,
            "📤 Nahrát obrázek",
            command=self._handle_upload_image,
            bg_color=COLORS["accent"],
            width=25,
            height=1
        ).pack(padx=10, pady=5)
    
    def _build_bottom(self, parent) -> None:
        """Vytvoří spodní akční tlačítka."""
        button_frame = tk.Frame(parent, bg=COLORS["bg_primary"])
        button_frame.pack(fill=tk.X, padx=20, pady=20)

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
        
        # Update listbox
        self.question_listbox.delete(0, tk.END)
        for q in filtered:
            self.question_listbox.insert(
                tk.END,
                f"[{q.id}] {q.category} ({q.difficulty})"
            )
        
        logger.info(f"Filtered to {len(filtered)} questions")
    
    def _on_question_select(self, event) -> None:
        """Zpracuje výběr otázky v seznamu."""
        selection = self.question_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        item_text = self.question_listbox.get(index)
        
        # Extract ID from text
        question_id = item_text.split('[')[1].split(']')[0]
        
        # Find question
        self.selected_question = self.loader.get_by_id(question_id)
        
        if self.selected_question:
            # Update preview
            self.preview_id.config(text=self.selected_question.id)
            self.preview_category.config(text=self.selected_question.category)
            self.preview_difficulty.config(text=self.selected_question.difficulty)
            self.preview_length.config(text=str(self.selected_question.answer_length))
            
            logger.info(f"Question selected: {question_id}")
    
    def _handle_upload_image(self) -> None:
        """Nahraje obrázek pro vybranou otázku."""
        if not self.selected_question:
            messagebox.showwarning("Chyba", "Prosím vyberte nejdříve otázku")
            return
        
        # Open file dialog
        file_path = filedialog.askopenfilename(
            title="Vyberte obrázek pro otázku",
            filetypes=[
                ("Obrázky", "*.jpg *.jpeg *.png *.gif *.webp"),
                ("JPEG", "*.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("GIF", "*.gif"),
                ("WebP", "*.webp"),
                ("Všechny soubory", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            # Upload image
            result = self.image_upload_service.upload_image(
                file_path=file_path,
                reference_name=self.selected_question.id
            )
            
            if result.get("success"):
                image_id = result.get("image_id")
                messagebox.showinfo(
                    "Úspěch",
                    f"Obrázek byl úspěšně nahrán.\nID: {image_id}"
                )
                logger.info(f"Image uploaded for question {self.selected_question.id}: {image_id}")
            else:
                error_msg = result.get("error", "Neznámá chyba")
                messagebox.showerror("Chyba", f"Nahrávání se nezdařilo: {error_msg}")
                logger.error(f"Nahrání obrázku selhalo: {error_msg}")
        
        except Exception as e:
            messagebox.showerror("Chyba", f"Chyba při nahrávání: {str(e)}")
            logger.error(f"Image upload exception: {e}")
    
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
