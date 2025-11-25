import tkinter as tk
from tkinter import messagebox
import random
import time
import json
import os

# Simple Memory Match (จับคู่การ์ด) — Tkinter prototype
# Accessibility notes:
# - Large buttons and fonts
# - Configurable grid size (rows x cols) and slow default timings
# - Saves score in data/scores.json

class MemoryMatchApp:
    def __init__(self, master, rows=2, cols=4, reveal_time=1000):
        self.master = master
        self.master.title("Memory Match - Vaila")
        self.rows = rows
        self.cols = cols
        self.reveal_time = reveal_time  # milliseconds to show unmatched pair
        self.num_pairs = (rows * cols) // 2

        # Symbols used for cards (use emoji / simple icons). Add more if needed.
        all_symbols = ['🐶','🐱','🐰','🦊','🐼','🐵','🐸','🐷','🍎','🍊','🍓','🌟']
        self.symbols = all_symbols[:self.num_pairs]

        self.cards = self.symbols * 2
        random.shuffle(self.cards)

        self.buttons = []
        self.flipped = []  # list of indices currently flipped
        self.matched = set()
        self.moves = 0
        self.start_time = time.time()

        # UI elements
        self.top_frame = tk.Frame(master)
        self.top_frame.pack(padx=10, pady=6)

        self.status_var = tk.StringVar()
        self.status_var.set("Moves: 0")
        self.status_label = tk.Label(self.top_frame, textvariable=self.status_var, font=(None, 18))
        self.status_label.pack(side=tk.LEFT, padx=8)

        self.timer_var = tk.StringVar()
        self.timer_var.set("Time: 0s")
        self.timer_label = tk.Label(self.top_frame, textvariable=self.timer_var, font=(None, 18))
        self.timer_label.pack(side=tk.LEFT, padx=8)

        self.reset_button = tk.Button(self.top_frame, text="Reset", command=self.reset_game, font=(None, 14))
        self.reset_button.pack(side=tk.LEFT, padx=8)

        # Vaila message area
        self.vaila_var = tk.StringVar()
        self.vaila_var.set("ยินดีต้อนรับ! คลิกการ์ดเพื่อเริ่มเล่น")
        # Vaila area: message + optional avatar image (assets/vaila.png)
        self.vaila_frame = tk.Frame(master)
        self.vaila_frame.pack(pady=(0,6), fill='x')
        self.vaila_label = tk.Label(self.vaila_frame, textvariable=self.vaila_var, font=(None, 16), fg="#2b5d9f")
        self.vaila_label.pack(side=tk.LEFT)
        # try load avatar image from assets, otherwise fallback to emoji/text
        self.avatar_img = None
        try:
            from PIL import Image, ImageTk
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            avatar_path = os.path.join(base_dir, 'assets', 'vaila.png')
            if os.path.exists(avatar_path):
                img = Image.open(avatar_path)
                img = img.resize((100, 100), Image.Resampling.LANCZOS)
                self.avatar_img = ImageTk.PhotoImage(img)
                self.avatar_label = tk.Label(self.vaila_frame, image=self.avatar_img, bg='white')
            else:
                raise FileNotFoundError
        except Exception:
            self.avatar_label = tk.Label(self.vaila_frame, text='🦊 ไวล่า', font=(None, 20), bg='white')
        self.avatar_label.pack(side=tk.RIGHT, padx=8)

        # Grid area
        self.grid_frame = tk.Frame(master)
        self.grid_frame.pack(padx=10, pady=10)

        self.create_grid()
        self.update_timer()

    def create_grid(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        self.buttons = []
        idx = 0
        for r in range(self.rows):
            for c in range(self.cols):
                b = tk.Button(self.grid_frame, text='?', width=6, height=3,
                              font=(None, 26), command=lambda i=idx: self.on_click(i))
                b.grid(row=r, column=c, padx=6, pady=6)
                self.buttons.append(b)
                idx += 1

    def on_click(self, idx):
        if idx in self.matched:
            return
        if idx in self.flipped:
            return
        if len(self.flipped) >= 2:
            return

        # reveal
        self.buttons[idx]['text'] = self.cards[idx]
        self.flipped.append(idx)

        if len(self.flipped) == 2:
            self.master.after(100, self.check_match)

    def check_match(self):
        i, j = self.flipped
        self.moves += 1
        self.status_var.set(f"Moves: {self.moves}")

        if self.cards[i] == self.cards[j]:
            # match found
            self.matched.add(i)
            self.matched.add(j)
            self.buttons[i]['state'] = tk.DISABLED
            self.buttons[j]['state'] = tk.DISABLED
            self.vaila_var.set("ดีมาก! เจอคู่แล้ว 🎉")
            self.flipped = []
            if len(self.matched) == len(self.cards):
                self.finish_game()
        else:
            # not a match — hide after reveal_time
            self.vaila_var.set("ลองอีกครั้งนะ")
            self.master.after(self.reveal_time, self.hide_unmatched)

    def hide_unmatched(self):
        for idx in self.flipped:
            self.buttons[idx]['text'] = '?'
        self.flipped = []

    def finish_game(self):
        elapsed = int(time.time() - self.start_time)
        msg = f"เล่นจบแล้ว! ใช้ {self.moves} ครั้ง เวลา {elapsed} วินาที."
        messagebox.showinfo("สำเร็จ", msg)
        self.vaila_var.set("เยี่ยมมาก! ไวล่าภูมิใจในตัวคุณ 🥳")
        # save score
        self.save_score(self.moves, elapsed)

    def save_score(self, moves, elapsed):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        data_dir = os.path.join(base_dir, 'data')
        os.makedirs(data_dir, exist_ok=True)
        scores_file = os.path.join(data_dir, 'scores.json')
        try:
            if os.path.exists(scores_file):
                with open(scores_file, 'r', encoding='utf-8') as f:
                    scores = json.load(f) or []
            else:
                scores = []
        except Exception:
            scores = []
        record = {
            'timestamp': int(time.time()),
            'moves': moves,
            'time_s': elapsed,
            'rows': self.rows,
            'cols': self.cols
        }
        scores.append(record)
        with open(scores_file, 'w', encoding='utf-8') as f:
            json.dump(scores, f, ensure_ascii=False, indent=2)

    def reset_game(self):
        # reinitialize game state
        random.shuffle(self.cards)
        self.flipped = []
        self.matched = set()
        self.moves = 0
        self.start_time = time.time()
        self.status_var.set("Moves: 0")
        self.vaila_var.set("เกมรีเซ็ตแล้ว — พร้อมเล่นใหม่")
        for b in self.buttons:
            b.config(text='?', state=tk.NORMAL)

    def update_timer(self):
        elapsed = int(time.time() - self.start_time)
        self.timer_var.set(f"Time: {elapsed}s")
        self.master.after(1000, self.update_timer)


if __name__ == '__main__':
    root = tk.Tk()
    # For accessibility, start with small grid (2x4 = 4 คู่) — use args to increase difficulty
    app = MemoryMatchApp(root, rows=2, cols=4, reveal_time=1200)
    root.mainloop()
