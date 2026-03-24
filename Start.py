# --- 遊戲啟動程式碼 (啟動流程) -----------------------------------------------
import tkinter as tk
from tkinter import messagebox
from controller import Controller

def start_game(text_x, text_y, text_ratio, setup_root: tk.Tk):
    """從設定視窗啟動遊戲。"""
    try:
        x = int(text_x)
        y = int(text_y)
        ratio = int(text_ratio) if text_ratio else 30
        
        if not (1 <= ratio <= 100):
            messagebox.showinfo("錯誤！", "答案格比例請輸入 1 到 100 的整數！")
            return
        if not (x > 0 and y > 0):
            messagebox.showinfo("錯誤！", "請輸入正確的網格大小！")
            return

        setup_root.destroy()
        # 啟動 Controller，由 Controller 創建遊戲主視窗
        game = Controller(x, y, ratio)
        
    except ValueError:
        messagebox.showerror("錯誤！", "請在所有欄位輸入有效的整數！")
    except Exception as e:
        messagebox.showerror("錯誤！", f"發生未知錯誤: {e}")

def initial_settings():
    """創建遊戲設定視窗。"""
    root = tk.Tk()
    root.title("Sum Game 遊戲設定")
    root.geometry("400x300")
    
    # 網格 X
    tk.Label(master=root, text="請輸入網格大小 (x):").grid(row=1, column=0, padx=5, pady=5, sticky='w')
    entry_x = tk.Entry(master=root)
    entry_x.grid(row=1, column=1, padx=5, pady=5)
    entry_x.insert(0, "5") # 預設值
    
    # 網格 Y
    tk.Label(master=root, text="請輸入網格大小 (y):").grid(row=2, column=0, padx=5, pady=5, sticky='w')
    entry_y = tk.Entry(master=root)
    entry_y.grid(row=2, column=1, padx=5, pady=5)
    entry_y.insert(0, "5") # 預設值
    
    # 答案格比例
    tk.Label(master=root, text="請輸入答案格比例 (%):").grid(row=3, column=0, padx=5, pady=5, sticky='w')
    entry_ratio = tk.Entry(master=root)
    entry_ratio.grid(row=3, column=1, padx=5, pady=5)
    entry_ratio.insert(0, "30") # 預設值
    
    # 開始按鈕
    button = tk.Button(master=root, text="開始遊戲！", 
                       command=lambda: start_game(entry_x.get(), entry_y.get(), entry_ratio.get(), root))
    button.grid(row=4, column=1, columnspan=2, padx=5, pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    initial_settings()
