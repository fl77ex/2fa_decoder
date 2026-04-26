import re
import time
import tkinter as tk
from tkinter import ttk
from urllib.parse import parse_qs, urlparse

import pyotp


WINDOW_TITLE = "2FA Decoder"
WINDOW_SIZE = "360x260"
BACKGROUND = "#f4f6f8"
ACCENT = "#0f6cbd"
SUCCESS = "#0f7b0f"
ERROR = "#b42318"
PLACEHOLDER_CODE = "------"
REFRESH_MS = 200
TOTP_PERIOD = 30


class TOTPApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.resizable(False, False)
        self.root.configure(bg=BACKGROUND)

        self.style = ttk.Style()
        self.style.theme_use("default")
        self.style.configure("TProgressbar", thickness=6, background=ACCENT)

        self.secret_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Click the field to paste a secret or otpauth URI.")
        self.code_var = tk.StringVar(value=PLACEHOLDER_CODE)
        self.timer_var = tk.StringVar(value="")

        self.secret = ""
        self.last_code = ""

        self.build_ui()

    def build_ui(self) -> None:
        container = tk.Frame(self.root, bg=BACKGROUND, padx=20, pady=18)
        container.pack(fill="both", expand=True)

        title = tk.Label(
            container,
            text="Current TOTP code",
            font=("Segoe UI", 10, "bold"),
            bg=BACKGROUND,
            fg="#4b5563",
        )
        title.pack(anchor="w")

        self.code_label = tk.Label(
            container,
            textvariable=self.code_var,
            font=("Segoe UI", 34, "bold"),
            bg=BACKGROUND,
            fg=ACCENT,
            cursor="hand2",
        )
        self.code_label.pack(pady=(6, 0))
        self.code_label.bind("<Button-1>", self.copy_code)

        timer_label = tk.Label(
            container,
            textvariable=self.timer_var,
            font=("Segoe UI", 9),
            bg=BACKGROUND,
            fg="#6b7280",
        )
        timer_label.pack(pady=(4, 10))

        self.entry = ttk.Entry(
            container,
            textvariable=self.secret_var,
            font=("Segoe UI", 11),
            width=34,
            state="readonly",
        )
        self.entry.pack(fill="x")
        self.entry.bind("<Button-1>", self.paste_from_clipboard)

        hint = tk.Label(
            container,
            text="Accepts raw Base32 secrets and otpauth:// URIs.",
            font=("Segoe UI", 9),
            bg=BACKGROUND,
            fg="#6b7280",
        )
        hint.pack(anchor="w", pady=(6, 10))

        self.notification = tk.Label(
            container,
            textvariable=self.status_var,
            font=("Segoe UI", 9),
            bg=BACKGROUND,
            fg=SUCCESS,
            wraplength=300,
            justify="left",
        )
        self.notification.pack(anchor="w")

        self.progress = ttk.Progressbar(
            container,
            orient="horizontal",
            mode="determinate",
            length=260,
            maximum=TOTP_PERIOD,
        )
        self.progress.pack(anchor="w", pady=(12, 0))

    def set_status(self, message: str, color: str = SUCCESS) -> None:
        self.status_var.set(message)
        self.notification.config(fg=color)

    def clean_secret(self, raw_value: str) -> str:
        return re.sub(r"[^A-Z2-7]", "", raw_value.upper())

    def extract_secret(self, raw_value: str) -> str:
        candidate = raw_value.strip()

        if candidate.lower().startswith("otpauth://"):
            parsed = urlparse(candidate)
            params = parse_qs(parsed.query)
            secret_values = params.get("secret", [])
            if secret_values:
                return self.clean_secret(secret_values[0])
            return ""

        return self.clean_secret(candidate)

    def paste_from_clipboard(self, event=None):
        try:
            clipboard_value = self.root.clipboard_get()
        except tk.TclError:
            self.set_status("Clipboard is empty or unavailable.", ERROR)
            return None

        extracted_secret = self.extract_secret(clipboard_value)
        if not extracted_secret:
            self.set_status("No valid TOTP secret found in the clipboard.", ERROR)
            return None

        if extracted_secret != self.secret:
            self.secret = extracted_secret
            self.secret_var.set(extracted_secret)
            self.set_status("Secret loaded from clipboard.")

        return None

    def copy_code(self, event=None):
        if not self.last_code:
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(self.last_code)
        self.set_status("Current code copied to clipboard.")

    def update_code_loop(self) -> None:
        if self.secret_var.get():
            self.secret = self.clean_secret(self.secret_var.get())
            try:
                totp = pyotp.TOTP(self.secret)
                code = totp.now()
                remaining = int(totp.interval - (time.time() % totp.interval))
            except (TypeError, ValueError):
                self.code_var.set("ERROR")
                self.timer_var.set("Invalid secret")
                self.progress["value"] = 0
                self.set_status("The secret could not be decoded.", ERROR)
            else:
                self.last_code = code
                self.code_var.set(code)
                self.timer_var.set(f"Refreshes in {remaining}s")
                self.progress["value"] = TOTP_PERIOD - remaining
        else:
            self.last_code = ""
            self.code_var.set(PLACEHOLDER_CODE)
            self.timer_var.set("")
            self.progress["value"] = 0

        self.root.after(REFRESH_MS, self.update_code_loop)


def main() -> None:
    root = tk.Tk()
    app = TOTPApp(root)
    app.update_code_loop()
    root.mainloop()


if __name__ == "__main__":
    main()
