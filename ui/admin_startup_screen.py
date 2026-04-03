"""Úvodní obrazovka aplikace s volbou režimu Administrace/Hra."""

import tkinter as tk
from tkinter import messagebox
import logging
from typing import Optional, Callable

from services.admin_auth import AdminAuth
from ui.admin_login_screen import AdminLoginScreen

logger = logging.getLogger(__name__)


class AdminStartupScreen:
    """Úvodní obrazovka s přechodem do hry nebo administrace."""

    def __init__(
        self,
        parent: tk.Widget,
        admin_auth: AdminAuth,
    ):
        """Inicializuje úvodní obrazovku."""
        self.parent = parent
        self.admin_auth = admin_auth
        self.on_admin_callback: Optional[Callable] = None
        self.on_play_callback: Optional[Callable] = None

        self.frame = tk.Frame(parent, bg="#2c3e50")
        self._build_ui()

    def _build_ui(self) -> None:
        """Vytvoří obsah úvodní obrazovky."""
        # Center content vertically and horizontally
        center_frame = tk.Frame(self.frame, bg="#0f172a")
        center_frame.pack(expand=True)

        # Title
        title_label = tk.Label(
            center_frame,
            text="INFORMAČNÍ KVÍZ",
            font=("Segoe UI", 36, "bold"),
            bg="#0f172a",
            fg="#f1f5f9",
        )
        title_label.pack(pady=20)

        # Subtitle
        subtitle_label = tk.Label(
            center_frame,
            text="SOUTĚŽ 2026",
            font=("Segoe UI", 18),
            bg="#0f172a",
            fg="#cbd5e1",
        )
        subtitle_label.pack(pady=(0, 40))

        # Buttons frame
        buttons_frame = tk.Frame(center_frame, bg="#0f172a")
        buttons_frame.pack(pady=20)

        # Admin button
        admin_button = tk.Button(
            buttons_frame,
            text="PŘÍSTUP ADMIN",
            command=self._on_admin_clicked,
            font=("Segoe UI", 12, "bold"),
            width=20,
            height=3,
            bg="#ef4444",
            fg="white",
            relief=tk.FLAT,
            bd=0,
            activebackground="#dc2626",
            activeforeground="white",
            cursor="hand2",
            padx=20,
            pady=15
        )
        admin_button.pack(side=tk.LEFT, padx=20)

        # Play button
        play_button = tk.Button(
            buttons_frame,
            text="HRÁT HRU",
            command=self._on_play_clicked,
            font=("Segoe UI", 12, "bold"),
            width=20,
            height=3,
            bg="#10b981",
            fg="white",
            relief=tk.FLAT,
            bd=0,
            activebackground="#059669",
            activeforeground="white",
            cursor="hand2",
            padx=20,
            pady=15
        )
        play_button.pack(side=tk.LEFT, padx=20)

        # Info frame at bottom
        info_frame = tk.Frame(self.frame, bg="#1a202c", height=50)
        info_frame.pack(fill=tk.X, side=tk.BOTTOM)

        info_label = tk.Label(
            info_frame,
            text="Interaktivní kvízová aplikace | Verze 2.0 | © SSPU 2026",
            font=("Segoe UI", 8),
            bg="#1a202c",
            fg="#64748b",
        )
        info_label.pack(pady=10)

    def _on_admin_clicked(self) -> None:
        """Zpracuje kliknutí na tlačítko Administrace."""
        logger.info("Kliknuto na Administrace - otevírám přihlášení")

        # Show login screen
        login_screen = AdminLoginScreen(
            self.parent,
            self.admin_auth,
            on_success=self._on_admin_success,
        )

        if login_screen.show():
            logger.info("Admin přihlášení bylo úspěšné")
            if self.on_admin_callback:
                self.on_admin_callback()
        else:
            logger.info("Admin přihlášení bylo zrušeno nebo selhalo")

    def _on_admin_success(self) -> None:
        """Hook po úspěšném admin přihlášení."""
        pass

    def _on_play_clicked(self) -> None:
        """Zpracuje kliknutí na tlačítko Hrát."""
        logger.info("Kliknuto na Hrát hru")

        if self.on_play_callback:
            self.on_play_callback()

    def show(
        self,
        on_admin: Optional[Callable] = None,
        on_play: Optional[Callable] = None,
    ) -> None:
        """Zobrazí úvodní obrazovku a nastaví callbacky."""
        self.on_admin_callback = on_admin
        self.on_play_callback = on_play
        self.frame.pack(fill=tk.BOTH, expand=True)

    def hide(self) -> None:
        """Skryje úvodní obrazovku."""
        self.frame.pack_forget()

    def destroy(self) -> None:
        """Zruší úvodní obrazovku."""
        self.frame.destroy()
