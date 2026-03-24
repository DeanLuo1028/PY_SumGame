# --- 2. View (Tkinter 介面元件) ------------------------------------------------
import tkinter as tk

class Tile(tk.Button):
    """View 元件：代表遊戲網格中的一個按鈕格子。"""
    def __init__(self, master, x, y, controller, model):
        # 為了避免循環依賴，View 只持有 Controller 和 Model 的實例
        self.controller = controller 
        self.model = model
        self.x = x
        self.y = y

        super().__init__(master, width=3, height=1, font=("Arial", 18), bg="white", fg="black")
        
        # 綁定事件到 Controller
        self.config(command=lambda: self.controller.handle_tile_click(self.x, self.y, 'left'))
        self.bind("<Button-3>", lambda event: self.controller.handle_tile_click(self.x, self.y, 'right'))
        self.grid(row=y, column=x)
        
        self.update_view() # 初始化時更新一次

    def update_view(self):
        """根據 Model 的數據更新按鈕的視覺狀態。"""
        tile_data = self.model.get_tile_data(self.x, self.y)
        
        self.config(text=str(tile_data['number']), state="normal")
        
        if self.model.is_game_over:
            # 遊戲結束時顯示正確/錯誤狀態
            if tile_data['is_answer']:
                self.config(bg="green", fg="white") # 答案
            else:
                self.config(bg="red", fg="white") # 非答案
            self.config(state="disabled")
            return

        if tile_data['is_selected']:
            self.config(bg="green" if tile_data['is_answer'] else "red", fg="white", state="disabled")
        elif tile_data['is_excluded']:
            # 已排除/標記
            self.config(text="X", bg="lightgrey", fg="red")
        else:
            # 初始狀態
            self.config(text=str(tile_data['number']), bg="white", fg="black")
            
class Title(tk.Label):
    """View 元件：顯示目標和 (上排/左排)。"""
    def __init__(self, master, controller, index, is_col):
        self.controller = controller
        self.index = index
        self.is_col = is_col
        
        target_sum = self.controller.model.calculate_target_sum(index, is_col)
        
        super().__init__(master=master, text=str(target_sum), width=3, font=("Arial", 18), 
                         bg="lightblue", fg="darkblue")

class SelectedTitle(tk.Label):
    """View 元件：顯示已選格子之和進度 (下排/右排)。"""
    def __init__(self, master, controller, index, is_col):
        self.controller = controller
        self.index = index
        self.is_col = is_col
        self.target_sum = self.controller.model.calculate_target_sum(index, is_col)
        
        super().__init__(master=master, width=5, font=("Arial", 18), bg="yellow", fg="black")
        self.update_view()

    def update_view(self):
        """根據 Model 的數據更新標籤的視覺狀態。"""
        NOA, NOS, current_sum = self.controller.model.calculate_selected_sum(self.index, self.is_col)
        
        # 顯示格式：目前總和 / 目標總和
        display_text = f"{current_sum} / {self.target_sum}"
        
        # 顏色邏輯：NOS == NOA 表示所有答案格子都已選中
        if NOA == 0:
            bg_color = "green" # 無答案格子，默認達成
        elif NOS == NOA:
            bg_color = "green"
        elif NOS == 0 and NOA > 0:
            bg_color = "yellow"
        else:
            bg_color = "orange"

        self.config(text=display_text, bg=bg_color, fg="white")

class ScoreLabel(tk.Label):
    """View 元件：顯示分數。"""
    def __init__(self, master, controller):
        self.controller = controller
        super().__init__(master=master, text="分數: 0", font=("Arial", 18), bg="pink", fg="gray")
        self.update_view()

    def update_view(self):
        self.config(text=f"分數: {self.controller.model.score}")