"""Hlavní administrační panel pro správu otázek."""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
from typing import Optional, Callable, List

from services.admin_question_manager import AdminQuestionManager
from services.image_upload_service import ImageUploadService

logger = logging.getLogger(__name__)


class AdminQuestionPanel:
    """Panel pro zobrazení, filtrování a správu otázek."""

    def __init__(
        self,
        parent: tk.Widget,
        question_manager: AdminQuestionManager,
        image_service: ImageUploadService,
        on_close: Optional[Callable] = None,
    ):
        """Inicializuje administrační panel otázek."""
        self.parent = parent
        self.manager = question_manager
        self.images = image_service
        self.on_close = on_close

        # Create main window
        self.window = tk.Toplevel(parent)
        self.window.title("Správa otázek")
        self.window.geometry("900x600")

        # Make modal
        self.window.transient(parent)
        self.window.grab_set()

        self._build_ui()
        self._refresh_questions_table()

    def _build_ui(self) -> None:
        """Vytvoří rozhraní panelu."""
        # Header frame
        header_frame = tk.Frame(self.window, bg="#f0f0f0", height=60)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)

        # Title
        title_label = tk.Label(
            header_frame,
            text="SPRÁVA OTÁZEK",
            font=("Helvetica", 14, "bold"),
            bg="#f0f0f0",
            fg="#333333",
        )
        title_label.pack(padx=20, pady=10, anchor=tk.W)

        # Filter frame
        filter_frame = tk.Frame(self.window, bg="white", height=50)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        filter_frame.pack_propagate(False)

        # Pole hledání
        search_label = tk.Label(
            filter_frame, text="Hledat:", font=("Helvetica", 9), bg="white"
        )
        search_label.pack(side=tk.LEFT, padx=(10, 5), pady=5)

        self.search_entry = tk.Entry(filter_frame, font=("Helvetica", 9), width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5, pady=5)

        # Filtr kategorie
        cat_label = tk.Label(
            filter_frame, text="Kategorie:", font=("Helvetica", 9), bg="white"
        )
        cat_label.pack(side=tk.LEFT, padx=(10, 5), pady=5)

        self.category_var = tk.StringVar(value="Vše")
        self.category_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.category_var,
            state="readonly",
            width=15,
            font=("Helvetica", 9),
        )
        self.category_combo.pack(side=tk.LEFT, padx=5, pady=5)

        # Filtr obtížnosti
        diff_label = tk.Label(
            filter_frame, text="Obtížnost:", font=("Helvetica", 9), bg="white"
        )
        diff_label.pack(side=tk.LEFT, padx=(10, 5), pady=5)

        self.difficulty_var = tk.StringVar(value="Vše")
        self.difficulty_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.difficulty_var,
            values=["Vše", "easy", "medium", "hard"],
            state="readonly",
            width=10,
            font=("Helvetica", 9),
        )
        self.difficulty_combo.pack(side=tk.LEFT, padx=5, pady=5)

        # Tlačítko hledání
        search_button = tk.Button(
            filter_frame,
            text="Hledat",
            command=self._refresh_questions_table,
            font=("Helvetica", 9),
            width=8,
            bg="#5cb85c",
            fg="white",
        )
        search_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Tabulka otázek
        table_frame = tk.Frame(self.window)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create Treeview table
        columns = ("ID", "Kategorie", "Obrázek", "Obtížnost", "Popis")
        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            height=15,
            show="tree headings",
        )

        # Define column headings and widths
        self.table.column("#0", width=0, stretch=tk.NO)
        self.table.column("ID", anchor=tk.W, width=50)
        self.table.column("Kategorie", anchor=tk.W, width=100)
        self.table.column("Obrázek", anchor=tk.W, width=100)
        self.table.column("Obtížnost", anchor=tk.CENTER, width=80)
        self.table.column("Popis", anchor=tk.W, width=400)

        self.table.heading("#0", text="", anchor=tk.W)
        self.table.heading("ID", text="ID", anchor=tk.W)
        self.table.heading("Kategorie", text="Kategorie", anchor=tk.W)
        self.table.heading("Obrázek", text="ID obrázku", anchor=tk.W)
        self.table.heading("Obtížnost", text="Obtížnost", anchor=tk.CENTER)
        self.table.heading("Popis", text="Popis", anchor=tk.W)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.table.yview)
        self.table.configure(yscroll=scrollbar.set)

        self.table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Button frame
        button_frame = tk.Frame(self.window, bg="white", height=50)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        button_frame.pack_propagate(False)

        new_button = tk.Button(
            button_frame,
            text="Nová otázka",
            command=self._on_new_question,
            font=("Helvetica", 9),
            bg="#5cb85c",
            fg="white",
            width=15,
        )
        new_button.pack(side=tk.LEFT, padx=5, pady=5)

        edit_button = tk.Button(
            button_frame,
            text="Upravit",
            command=self._on_edit_question,
            font=("Helvetica", 9),
            bg="#0275d8",
            fg="white",
            width=10,
        )
        edit_button.pack(side=tk.LEFT, padx=5, pady=5)

        delete_button = tk.Button(
            button_frame,
            text="Smazat",
            command=self._on_delete_question,
            font=("Helvetica", 9),
            bg="#d9534f",
            fg="white",
            width=10,
        )
        delete_button.pack(side=tk.LEFT, padx=5, pady=5)

        upload_button = tk.Button(
            button_frame,
            text="Nahrát obrázek",
            command=self._on_upload_image,
            font=("Helvetica", 9),
            bg="#f0ad4e",
            fg="white",
            width=15,
        )
        upload_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Status frame
        status_frame = tk.Frame(self.window, bg="#f0f0f0", height=40)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        status_frame.pack_propagate(False)

        self.status_label = tk.Label(
            status_frame,
            text="",
            font=("Helvetica", 9),
            bg="#f0f0f0",
            fg="#666666",
            justify=tk.LEFT,
        )
        self.status_label.pack(anchor=tk.W, pady=5)

        # Footer frame
        footer_frame = tk.Frame(self.window, bg="white")
        footer_frame.pack(fill=tk.X, padx=10, pady=5)

        close_button = tk.Button(
            footer_frame,
            text="Zpět na úvod",
            command=self._on_close,
            font=("Helvetica", 9),
            width=20,
            bg="#ffffff",
            fg="#333333",
        )
        close_button.pack(side=tk.LEFT)

        # Update category combo with available categories
        self._update_category_combo()

    def _update_category_combo(self) -> None:
        """Aktualizuje seznam kategorií ve filtru."""
        stats = self.manager.get_statistics()
        categories = ["Vše"] + list(stats.get("by_category", {}).keys())
        self.category_combo["values"] = categories

    def _refresh_questions_table(self) -> None:
        """Načte a zobrazí otázky podle aktivních filtrů."""
        # Clear existing items
        for item in self.table.get_children():
            self.table.delete(item)

        # Get questions
        questions = self.manager.get_all_questions()

        # Apply filters
        filtered = self._apply_filters(questions)

        # Add to table
        for q in filtered:
            self.table.insert(
                "",
                tk.END,
                values=(
                    q.get("id", ""),
                    q.get("category", ""),
                    q.get("image_id", ""),
                    q.get("difficulty", ""),
                    q.get("description", "")[:50],
                ),
            )

        # Update status
        self._update_status()

    def _apply_filters(self, questions: List) -> List:
        """Použije textový filtr, kategorii a obtížnost."""
        filtered = questions

        # Search filter
        search_term = self.search_entry.get().lower()
        if search_term:
            filtered = [
                q for q in filtered
                if search_term in q.get("id", "").lower()
                or search_term in q.get("description", "").lower()
                or search_term in q.get("image_id", "").lower()
            ]

        # Filtr kategorie
        category = self.category_var.get()
        if category != "Vše":
            filtered = [q for q in filtered if q.get("category") == category]

        # Filtr obtížnosti
        difficulty = self.difficulty_var.get()
        if difficulty != "Vše":
            filtered = [q for q in filtered if q.get("difficulty") == difficulty]

        return filtered

    def _update_status(self) -> None:
        """Aktualizuje stavový řádek panelu."""
        stats = self.manager.get_statistics()
        total = stats.get("total_questions", 0)
        by_cat = stats.get("by_category", {})

        cat_str = ", ".join(f"{k} ({v})" for k, v in sorted(by_cat.items()))
        status_text = f"Celkem: {total} | {cat_str}" if cat_str else f"Celkem: {total}"

        self.status_label.config(text=status_text)

    def _on_new_question(self) -> None:
        """Zpracuje přidání nové otázky."""
        messagebox.showinfo(
            "Nová otázka",
            "Zde se otevře formulář pro vytvoření otázky.\n"
            "(Funkce bude doplněna)",
            parent=self.window,
        )

    def _on_edit_question(self) -> None:
        """Zpracuje úpravu vybrané otázky."""
        selection = self.table.selection()
        if not selection:
            messagebox.showwarning(
                "Bez výběru",
                "Nejprve vyberte otázku k úpravě.",
                parent=self.window,
            )
            return

        question_id = self.table.item(selection[0])["values"][0]
        messagebox.showinfo(
            "Úprava otázky",
            f"Zde se otevře formulář pro úpravu otázky {question_id}.\n"
            "(Funkce bude doplněna)",
            parent=self.window,
        )

    def _on_delete_question(self) -> None:
        """Zpracuje smazání vybrané otázky."""
        selection = self.table.selection()
        if not selection:
            messagebox.showwarning(
                "Bez výběru",
                "Nejprve vyberte otázku ke smazání.",
                parent=self.window,
            )
            return

        question_id = self.table.item(selection[0])["values"][0]

        # Potvrzení smazání
        if messagebox.askyesno(
            "Potvrzení smazání",
            f"Opravdu chcete smazat otázku {question_id}?",
            parent=self.window,
        ):
            if self.manager.delete_question(question_id):
                messagebox.showinfo("Hotovo", "Otázka byla smazána.", parent=self.window)
                self._refresh_questions_table()
            else:
                messagebox.showerror("Chyba", "Otázku se nepodařilo smazat.", parent=self.window)

    def _on_upload_image(self) -> None:
        """Zpracuje nahrání obrázku."""
        file_path = filedialog.askopenfilename(
            parent=self.window,
            title="Vyberte soubor s obrázkem",
            filetypes=[
                ("Obrázky", "*.jpg *.jpeg *.png *.gif *.webp"),
                ("Všechny soubory", "*.*"),
            ],
        )

        if not file_path:
            return

        result = self.images.upload_image(file_path)

        if result["success"]:
            messagebox.showinfo(
                "Nahrání úspěšné",
                f"Obrázek byl nahrán: {result['image_id']}",
                parent=self.window,
            )
        else:
            messagebox.showerror(
                "Nahrání selhalo",
                f"Chyba: {result.get('error', 'Neznámá chyba')}",
                parent=self.window,
            )

    def _on_close(self) -> None:
        """Zavře panel správy otázek."""
        if self.on_close:
            self.on_close()
        self.window.destroy()

    def show(self) -> None:
        """Zobrazí panel jako modální okno."""
        self.parent.wait_window(self.window)
