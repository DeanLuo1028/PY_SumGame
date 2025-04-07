'''
import tkinter as tk

def popup(event):
    popup_menu.post(event.x_root, event.y_root)  # 顯示選單

def func(n):
    print(n)

root = tk.Tk()
root.geometry("300x200")

popup_menu = tk.Menu(root, tearoff=0)
for i in range(10):
    popup_menu.add_command(label=f"數字{i+1}", command=lambda: func(i+1))

root.bind("<Button-3>", popup)  # 右鍵綁定選單彈出

root.mainloop()
以上是錯的'''

import tkinter as tk

def popup(event):
    popup_menu.post(event.x_root, event.y_root)  # 顯示選單

def func(n):
    print(n)

root = tk.Tk()
root.geometry("300x200")

popup_menu = tk.Menu(root, tearoff=0)
for i in range(10):
    popup_menu.add_command(label=f"數字{i+1}", command=lambda n=i+1: func(n))  # 使用 n=i+1 凍結值

root.bind("<Button-3>", popup)  # 右鍵綁定選單彈出

root.mainloop()
