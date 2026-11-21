import os
import threading
import tkinter as tk
from tkinter import messagebox

try:
    import anthropic
except ImportError:
    anthropic = None

MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")
API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
DAILY = os.getenv("CLAWD_DAILY_REMAINING", "Not connected")
WEEKLY = os.getenv("CLAWD_WEEKLY_REMAINING", "Not connected")

class ClawdApp:
    def __init__(self, root):
        self.root = root
        root.title("Clawd")
        root.geometry("360x420")
        root.resizable(False, False)
        root.configure(bg="#211b2b")
        self.busy = False

        tk.Label(root, text="૮ ˶ᵔ ᵕ ᵔ˶ ა", font=("Segoe UI Emoji", 34), bg="#211b2b", fg="#ffb879").pack(pady=(12, 0))
        tk.Label(root, text="Clawd", font=("Segoe UI", 18, "bold"), bg="#211b2b", fg="#ffe1c3").pack()
        self.bubble = tk.Label(root, text="Hej! Daj mi zadanie 🧡", wraplength=310, justify="center", font=("Segoe UI", 11), bg="#392d48", fg="white", padx=16, pady=14)
        self.bubble.pack(padx=16, pady=12, fill="x")

        tk.Label(root, text=f"5h limit: {DAILY}     Weekly: {WEEKLY}", bg="#211b2b", fg="#bcb2c9", font=("Segoe UI", 9)).pack(pady=(0, 10))
        self.entry = tk.Text(root, height=4, wrap="word", bg="#31283c", fg="white", insertbackground="white", relief="flat", padx=10, pady=8)
        self.entry.pack(padx=16, fill="x")
        self.entry.insert("1.0", "")
        self.button = tk.Button(root, text="Send task", command=self.submit, bg="#ffb879", fg="#281b2b", relief="flat", font=("Segoe UI", 10, "bold"), padx=12, pady=8)
        self.button.pack(pady=12)
        tk.Label(root, text="API usage only · no MCP tools yet", bg="#211b2b", fg="#92869f", font=("Segoe UI", 8)).pack(side="bottom", pady=10)

    def submit(self):
        task = self.entry.get("1.0", "end").strip()
        if not task or self.busy:
            return
        if not API_KEY:
            messagebox.showerror("API key missing", "Set ANTHROPIC_API_KEY in your environment, then restart Clawd.")
            return
        if anthropic is None:
            messagebox.showerror("Dependency missing", "Install requirements with: python -m pip install -r requirements.txt")
            return
        self.busy = True
        self.button.config(state="disabled", text="Claude is working…")
        self.bubble.config(text="Okej! Myślę nad tym… ✨")
        threading.Thread(target=self.work, args=(task,), daemon=True).start()

    def work(self, task):
        try:
            client = anthropic.Anthropic(api_key=API_KEY)
            response = client.messages.create(model=MODEL, max_tokens=1200, messages=[{"role": "user", "content": task}])
            answer = "".join(block.text for block in response.content if getattr(block, "type", None) == "text")
            self.root.after(0, lambda: self.done(answer or "Gotowe!"))
        except Exception as exc:
            self.root.after(0, lambda: self.done(f"Ups, coś nie wyszło: {exc}"))

    def done(self, text):
        self.bubble.config(text=text[:800])
        self.button.config(state="normal", text="Send task")
        self.busy = False

if __name__ == "__main__":
    root = tk.Tk()
    ClawdApp(root)
    root.mainloop()
