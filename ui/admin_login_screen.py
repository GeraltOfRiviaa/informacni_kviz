"""Přihlašovací dialog pro přístup do administrace."""

import tkinter as tk
from tkinter import messagebox
import logging
from typing import Optional, Callable

from services.admin_auth import AdminAuth
from admin.constants import ADMIN_MAX_LOGIN_ATTEMPTS, ADMIN_LOCKOUT_DURATION_SECONDS

logger = logging.getLogger(__name__)


class AdminLoginScreen:
    """Modální dialog pro ověření správce."""

    def __init__(
        self,
        parent: tk.Widget,
        admin_auth: AdminAuth,
        on_success: Optional[Callable] = None,
    ):
        """Inicializuje přihlašovací dialog správce."""
        self.parent = parent
        self.admin_auth = admin_auth
        self.on_success = on_success
        self.result = False

        # Create modal window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Přístup do administrace")
        self.dialog.geometry("400x250")
        self.dialog.resizable(False, False)

        # Make modal (blocks parent)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center on parent
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 200
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 125
        self.dialog.geometry(f"+{x}+{y}")

        self._build_ui()
        self._update_status()

    def _build_ui(self) -> None:
        """Vytvoří přihlašovací formulář."""
        # Main padding frame
        main_frame = tk.Frame(self.dialog, bg="#f0f0f0", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = tk.Label(
            main_frame,
            text="PŘÍSTUP DO ADMINISTRACE",
            font=("Helvetica", 14, "bold"),
            bg="#f0f0f0",
            fg="#333333",
        )
        title_label.pack(pady=(0, 15))

        # Status frame (for lockout/error messages)
        self.status_frame = tk.Frame(main_frame, bg="#f0f0f0")
        self.status_frame.pack(fill=tk.X, pady=(0, 10))

        self.status_label = tk.Label(
            self.status_frame,
            text="",
            font=("Helvetica", 9),
            bg="#f0f0f0",
            fg="#d9534f",
            wraplength=360,
            justify=tk.LEFT,
        )
        self.status_label.pack(anchor=tk.W)

        # Password label
        pwd_label = tk.Label(
            main_frame,
            text="Heslo administrátora:",
            font=("Helvetica", 10),
            bg="#f0f0f0",
            fg="#333333",
        )
        pwd_label.pack(anchor=tk.W, pady=(10, 5))

        # Password input frame
        pwd_frame = tk.Frame(main_frame, bg="#f0f0f0")
        pwd_frame.pack(fill=tk.X, pady=(0, 15))

        self.password_entry = tk.Entry(
            pwd_frame,
            font=("Helvetica", 11),
            show="•",
            width=30,
        )
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        # Tlačítko pro zobrazení/skrytí hesla
        self.show_button = tk.Button(
            pwd_frame,
            text="Zobrazit",
            command=self._toggle_password_visibility,
            font=("Helvetica", 9),
            width=8,
            bg="#ffffff",
            fg="#333333",
            relief=tk.RAISED,
            bd=1,
        )
        self.show_button.pack(side=tk.LEFT)

        # Button frame
        button_frame = tk.Frame(main_frame, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, pady=(10, 0))

        self.login_button = tk.Button(
            button_frame,
            text="Přihlásit",
            command=self._on_login,
            font=("Helvetica", 10, "bold"),
            bg="#5cb85c",
            fg="white",
            width=10,
            relief=tk.RAISED,
            bd=1,
        )
        self.login_button.pack(side=tk.LEFT, padx=(0, 10))

        cancel_button = tk.Button(
            button_frame,
            text="Zrušit",
            command=self._on_cancel,
            font=("Helvetica", 10),
            bg="#ffffff",
            fg="#333333",
            width=10,
            relief=tk.RAISED,
            bd=1,
        )
        cancel_button.pack(side=tk.LEFT)

        # Informační řádek
        info_frame = tk.Frame(main_frame, bg="#f0f0f0")
        info_frame.pack(fill=tk.X, pady=(15, 0))

        self.attempts_label = tk.Label(
            info_frame,
            text="",
            font=("Helvetica", 9),
            bg="#f0f0f0",
            fg="#666666",
        )
        self.attempts_label.pack(anchor=tk.W)

        # Key bindings
        self.password_entry.bind("<Return>", lambda e: self._on_login())
        self.password_entry.bind("<Escape>", lambda e: self._on_cancel())

        # Focus password field
        self.password_entry.focus()

    def _toggle_password_visibility(self) -> None:
        """Přepne viditelnost hesla."""
        current_show = self.password_entry.cget("show")
        if current_show == "•":
            self.password_entry.config(show="")
            self.show_button.config(text="Skrýt")
        else:
            self.password_entry.config(show="•")
            self.show_button.config(text="Zobrazit")

    def _update_status(self) -> None:
        """Aktualizuje stavové informace podle přihlášení."""
        if self.admin_auth.is_locked():
            remaining = self.admin_auth.get_lockout_remaining_seconds()
            self.status_label.config(
                text=f"❌ Účet je zablokován. Zkuste znovu za {remaining} sekund",
                fg="#d9534f",
            )
            self.login_button.config(state=tk.DISABLED, bg="#cccccc")
            self.password_entry.config(state=tk.DISABLED)
        else:
            self.status_label.config(text="")
            self.login_button.config(state=tk.NORMAL, bg="#5cb85c")
            self.password_entry.config(state=tk.NORMAL)

        # Update attempts counter
        attempts_left = ADMIN_MAX_LOGIN_ATTEMPTS - self.admin_auth.failed_attempts
        if attempts_left > 0:
            self.attempts_label.config(
                text=f"Zbývající pokusy: {attempts_left}",
                fg="#666666",
            )
        else:
            self.attempts_label.config(
                text="Překročen maximální počet pokusů.",
                fg="#d9534f",
            )

    def _on_login(self) -> None:
        """Zpracuje kliknutí na tlačítko Přihlásit."""
        password = self.password_entry.get()

        if not password:
            messagebox.showwarning(
                "Vstup vyžadován",
                "Zadejte heslo.",
                parent=self.dialog,
            )
            self.password_entry.focus()
            return

        # Verify password
        if self.admin_auth.verify_password(password):
            logger.info("Admin přihlášení bylo úspěšné")
            self.result = True

            if self.on_success:
                self.on_success()

            self.dialog.destroy()
        else:
            # Přihlášení selhalo
            self._update_status()

            if self.admin_auth.is_locked():
                messagebox.showerror(
                    "Účet zablokován",
                    f"Příliš mnoho neúspěšných pokusů. "
                    f"Účet je zablokován na {ADMIN_LOCKOUT_DURATION_SECONDS // 60} minut.",
                    parent=self.dialog,
                )
                self.dialog.destroy()
            else:
                messagebox.showerror(
                    "Přihlášení selhalo",
                    "Nesprávné heslo. Zkuste to znovu.",
                    parent=self.dialog,
                )
                self.password_entry.delete(0, tk.END)
                self.password_entry.focus()

    def _on_cancel(self) -> None:
        """Zavře dialog bez přihlášení."""
        logger.info("Admin přihlášení bylo zrušeno")
        self.result = False
        self.dialog.destroy()

    def show(self) -> bool:
        """Zobrazí dialog a vrátí výsledek přihlášení."""
        self.parent.wait_window(self.dialog)
        return self.result
