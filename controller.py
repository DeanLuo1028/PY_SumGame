# --- 3. Controller (協調 Model 和 View) ---------------------------------------
import tkinter as tk
from tkinter import messagebox
from model import SumGameModel
from view import *

class SumGameController:
    """
    遊戲控制器：處理使用者輸入，更新 Model，並通知 View 刷新。
    """
    def __init__(self, x_range, y_range, ratio):
        self.model = SumGameModel(x_range, y_range, ratio)
        self.root = tk.Tk()
        self.root.title("Sum Game")
        
        # 儲存 View 元件以方便更新
        self.tile_views: list[list[Tile]] = [[None for _ in range(y_range)] for _ in range(x_range)]
        self.selected_sum_labels_col = [] # 下排
        self.selected_sum_labels_row = [] # 右排
        self.score_label: ScoreLabel = None

        self._setup_view()
        self.root.mainloop()

    def _setup_view(self):
        """建立所有 Tkinter 介面元件並佈局。"""
        Xrange, Yrange = self.model.Xrange, self.model.Yrange

        # 1. 遊戲主體框架
        main_frame = tk.Frame(self.root)
        main_frame.grid(row=1, column=1, columnspan=Xrange + 2, rowspan=Yrange + 2, padx=10, pady=10)

        # 2. 創建 Tile (格子)
        board = tk.Frame(main_frame)
        board.grid(row=1, column=1, columnspan=Xrange, rowspan=Yrange)
        for x in range(Xrange):
            for y in range(Yrange):
                tile = Tile(board, x, y, self, self.model)
                self.tile_views[x][y] = tile

        # 3. 創建 Title (目標和標籤)
        # 上排 (Column Target Sum)
        for x in range(Xrange):
            label = Title(main_frame, self, x, is_col=True)
            label.grid(row=0, column=x + 1, pady=(0, 5)) 

        # 左排 (Row Target Sum)
        for y in range(Yrange):
            label = Title(main_frame, self, y, is_col=False)
            label.grid(row=y + 1, column=0, padx=(0, 5))

        # 4. 創建 SelectedTitle (進度總和標籤)
        # 下排 (Column Selected Sum)
        for x in range(Xrange):
            label = SelectedTitle(main_frame, self, x, is_col=True)
            label.grid(row=Yrange + 1, column=x + 1, pady=(5, 0))
            self.selected_sum_labels_col.append(label)

        # 右排 (Row Selected Sum)
        for y in range(Yrange):
            label = SelectedTitle(main_frame, self, y, is_col=False)
            label.grid(row=y + 1, column=Xrange + 1, padx=(5, 0))
            self.selected_sum_labels_row.append(label)
        
        # 5. 控制面板
        panel = tk.Frame(self.root)
        panel.grid(row=Yrange + 3, column=1, columnspan=Xrange + 2, pady=10)

        prompt_button = tk.Button(master=panel, text="提示 (-1 分)", font=("Arial", 18), bg="green", fg="white", 
                                  command=self.handle_prompt)
        prompt_button.pack(side=tk.LEFT, padx=10)
        
        self.score_label = ScoreLabel(panel, self)
        self.score_label.pack(side=tk.LEFT, padx=10)
        
        restart_button = tk.Button(master=panel, text="重新開始", font=("Arial", 18), bg="blue", fg="white", 
                                   command=self.handle_restart)
        restart_button.pack(side=tk.LEFT, padx=10)

    def _update_all_views(self):
        """通知所有相關 View 刷新顯示。"""
        # 更新所有格子
        Xrange, Yrange = self.model.Xrange, self.model.Yrange
        for x in range(Xrange):
            for y in range(Yrange):
                self.tile_views[x][y].update_view()
        
        # 更新所有 SelectedTitle
        for label in self.selected_sum_labels_col + self.selected_sum_labels_row:
            label.update_view()
            
        # 更新分數
        self.score_label.update_view()
        
        # 檢查勝利
        if self.model.check_win():
            self._handle_win()

    # --- Controller 事件處理方法 ---
    
    def handle_tile_click(self, x, y, button_type):
        """處理格子點擊事件。"""
        is_fail = False
        
        if button_type == 'left':
            is_fail = self.model.handle_left_click(x, y)
        elif button_type == 'right':
            is_fail = self.model.handle_right_click(x, y)
        
        if is_fail:
            self._handle_lose()
        
        self._update_all_views() # 無論成功或失敗，都刷新介面

    def handle_prompt(self):
        """處理提示按鈕點擊事件。"""
        prompt_coords = self.model.use_prompt()
        if prompt_coords:
            self.tile_views[prompt_coords[0]][prompt_coords[1]].flash() # 給予閃爍提示
            self._update_all_views()
        else:
            messagebox.showinfo("提示", "無法使用提示，遊戲已結束或已選完所有答案。")

    def handle_restart(self):
        """重新啟動遊戲。"""
        self.root.destroy()
        from Start import main_init
        # 重新啟動設定流程
        main_init()
        
    def _handle_win(self):
        """處理獲勝邏輯。"""
        self.model.is_game_over = True
        messagebox.showinfo("你贏了", f"恭喜你贏得了遊戲！最終得分: {self.model.score}")


    def _handle_lose(self):
        """處理失敗邏輯。"""
        self.model.is_game_over = True
        messagebox.showinfo("你輸了", "你選了錯誤的格子或清除了答案格子。遊戲結束！")

