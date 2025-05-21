import tkinter as tk
from tkinter import ttk
import pyotp
import time
import re

class TOTPApp:
    def __init__(self, root):
        self.root = root
        self.root.title("2FA by @fl77ex")
        self.root.geometry("300x200")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")

        self.style = ttk.Style()
        self.style.theme_use("default")
        self.style.configure("TProgressbar", thickness=5, background="#0078D7")

        self.secret_var = tk.StringVar()
        self.secret = ""
        self.last_code = ""

        # CODE DISPLAY
        self.code_label = tk.Label(root, text="------", font=("Segoe UI", 36, "bold"),
                                   bg="#f0f0f0", fg="#0078D7", cursor="hand2")
        self.code_label.pack(pady=(20, 5))
        self.code_label.bind("<Button-1>", self.copy_code)

        # INPUT - readonly, запрещаем ручной ввод
        self.entry = ttk.Entry(root, textvariable=self.secret_var, font=("Segoe UI", 12), width=18, state="readonly")
        self.entry.pack(pady=5)

        # При клике в поле вставляем из буфера обмена
        self.entry.bind("<Button-1>", self.paste_from_clipboard)

        # NOTIFICATION
        self.notification = tk.Label(root, text="", font=("Segoe UI", 10), bg="#f0f0f0", fg="green")
        self.notification.pack()

        # PROGRESS BAR
        self.progress = ttk.Progressbar(root, orient="horizontal", mode="determinate", length=160, maximum=30)
        self.progress.pack(pady=5)

    def clean_secret(self, raw):
        return re.sub(r'[^A-Z2-7]', '', raw.upper())

    def paste_from_clipboard(self, event=None):
        try:
            current_clipboard = self.root.clipboard_get()
            clean = self.clean_secret(current_clipboard)
            if clean and clean != self.secret:
                self.secret_var.set(clean)
                self.secret = clean
        except:
            pass
        # Не блокируем стандартный обработчик клика
        return None

    def copy_code(self, event=None):
        if self.last_code:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.last_code)
            self.notification.config(text="Copied!")
            self.root.after(1000, lambda: self.notification.config(text=""))

    def update_code_loop(self):
        if self.secret_var.get():
            self.secret = self.clean_secret(self.secret_var.get())
            try:
                totp = pyotp.TOTP(self.secret)
                code = totp.now()
                self.last_code = code
                self.code_label.config(text=code)
                remaining = totp.interval - (time.time() % totp.interval)
                self.progress["value"] = 30 - remaining
            except:
                self.code_label.config(text="ERROR")
        else:
            self.code_label.config(text="------")
            self.progress["value"] = 0

        self.root.after(200, self.update_code_loop)

if __name__ == "__main__":
    root = tk.Tk()
    app = TOTPApp(root)
    app.update_code_loop()
    root.mainloop()
