import tkinter as tk
import random
from tkinter import messagebox

class ImageMemoryGame:
    def __init__(self, master):
        self.master = master
        self.master.title("เกมจับคู่ภาพสัตว์ (Emoji)")
        self.master.geometry("450x550")

        # ใช้ Emoji แทนรูปภาพเพื่อความง่าย
        # 'หมู', 'สุนัข', 'ไก่', 'นก', 'ปลา', 'มด', 'หมี', 'หนู'
        self.animal_emojis = ['🐷', '🐶', '🐔', '🐦', '🐟', '🐜', '🐻', '🐭']
        
        # สร้างรายการการ์ดโดยมีสัตว์แต่ละชนิด 2 ตัว
        self.card_values = self.animal_emojis * 2
        
        self.setup_game()

    def setup_game(self):
        # สับการ์ด
        random.shuffle(self.card_values)

        # ตัวแปรสำหรับติดตามสถานะเกม
        self.revealed_cards = []
        self.matched_pairs = 0
        self.buttons = {} # ใช้ dictionary เพื่อเก็บปุ่มและสถานะ
        self.is_checking = False # ป้องกันการคลิกเร็วเกินไป

        # สร้าง Frame สำหรับการ์ด
        card_frame = tk.Frame(self.master)
        card_frame.pack(pady=10)

        # สร้างปุ่มสำหรับการ์ด 4x4
        for i in range(16):
            row, col = divmod(i, 4)
            # ใช้ font ที่รองรับ emoji เช่น 'Segoe UI Emoji'
            button = tk.Button(card_frame, text='❓', font=('Segoe UI Emoji', 24), width=4, height=2,
                               command=lambda i=i: self.on_card_click(i))
            button.grid(row=row, column=col, padx=5, pady=5)
            self.buttons[i] = button

        # ปุ่มเริ่มใหม่
        restart_button = tk.Button(self.master, text="เริ่มใหม่", font=('Arial', 14), command=self.restart_game)
        restart_button.pack(pady=10)

    def on_card_click(self, index):
        # ถ้ากำลังรอเช็คคู่ หรือการ์ดถูกเปิดค้างไว้แล้ว ไม่ต้องทำอะไร
        if self.is_checking or self.buttons[index]['state'] == 'disabled':
            return

        button = self.buttons[index]
        value = self.card_values[index]
        button.config(text=value) # แสดง Emoji
        self.revealed_cards.append({'index': index, 'value': value})

        # ถ้าเปิดครบ 2 ใบแล้ว
        if len(self.revealed_cards) == 2:
            self.is_checking = True
            self.master.after(1000, self.check_match) # รอ 1 วินาทีแล้วค่อยเช็ค

    def check_match(self):
        card1 = self.revealed_cards[0]
        card2 = self.revealed_cards[1]

        if card1['value'] == card2['value']: # ถ้าจับคู่สำเร็จ
            self.matched_pairs += 1
            # ปิดการใช้งานปุ่มที่คู่กันแล้ว
            self.buttons[card1['index']].config(state='disabled')
            self.buttons[card2['index']].config(state='disabled')
            if self.matched_pairs == len(self.animal_emojis):
                messagebox.showinfo("ยินดีด้วย!", "คุณชนะแล้ว!")
        else: # ถ้าไม่ตรงกัน
            # พลิกการ์ดกลับเป็น '❓'
            self.buttons[card1['index']].config(text='❓')
            self.buttons[card2['index']].config(text='❓')

        self.revealed_cards = []
        self.is_checking = False

    def restart_game(self):
        # สับการ์ดใหม่
        random.shuffle(self.card_values)

        # รีเซ็ตสถานะเกม
        self.revealed_cards = []
        self.matched_pairs = 0
        self.is_checking = False

        # รีเซ็ตปุ่มทั้งหมดให้กลับเป็นสถานะเริ่มต้น
        for i in range(16):
            button = self.buttons[i]
            button.config(text='❓', state='normal')

if __name__ == "__main__":
    root = tk.Tk()
    game = ImageMemoryGame(root)
    root.mainloop()