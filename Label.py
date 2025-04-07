import tkinter as tk

# 創建主視窗
root = tk.Tk()
root.title("Label 範例")
root.geometry("300x200")

# 創建 Label
label = tk.Label(root, text="Hello, Tkinter!", font=("Arial", 16), bg="lightblue", fg="darkblue")
label.pack(pady=20)  # 使用 pack 進行版面配置

# 開始主迴圈
root.mainloop()
