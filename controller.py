# --- Controller (協調 Model 和 View) -----------------------------------------------
from tkinter import messagebox
from model import SumGame
from view import GameView


class Controller:
    """
    遊戲控制器：協調 Model 和 View。
    所有事件處理和邏輯協調都在這裡進行。
    """
    def __init__(self, x_range: int, y_range: int, ratio: int):
        """初始化控制器，創建 Model 和 View 並啟動主事件循環。

        Args:
            x_range (int): 橫向格子數量。
            y_range (int): 縱向格子數量。
            ratio (int): 答案格子比例百分比。
        """
        # 初始化 Model
        self.model = SumGame(x_range, y_range, ratio)
        
        # 初始化 View
        self.view = GameView(self.model, self)
        
        # 啟動事件迴圈
        self.view.mainloop()

    def _update_all_views(self) -> None:
        """通知所有相關 View 刷新顯示。"""
        self.view.update_all_tiles()
        self.view.update_selected_sum_labels()
        self.view.update_score_label()
        
        # 檢查勝利
        if self.model.check_win():
            self._handle_win()

    # --- 事件處理方法 ---

    def handle_tile_click(self, x: int, y: int, button_type: str) -> None:
        """處理格子點擊事件。

        Args:
            x (int): 點擊格子的列索引。
            y (int): 點擊格子的行索引。
            button_type (str): 按鍵類型，'left' 或 'right'。
        """
        is_fail = False
        
        if button_type == 'left':
            is_fail = self.model.handle_left_click(x, y)
        elif button_type == 'right':
            is_fail = self.model.handle_right_click(x, y)
        
        if is_fail:
            self._handle_lose()
        
        self._update_all_views()

    def handle_prompt(self) -> None:
        """處理提示按鈕點擊事件。"""
        prompt_coords = self.model.use_prompt()
        if prompt_coords:
            self.view.flash_tile(prompt_coords[0], prompt_coords[1])
            self._update_all_views()
        else:
            self.view.show_message("提示", "無法使用提示，遊戲已結束或已選完所有答案。")

    def handle_restart(self) -> None:
        """重新啟動遊戲。"""
        self.view.destroy()
        from Start import initial_settings
        initial_settings()

    def _handle_win(self):
        """處理獲勝邏輯。"""
        self.model.is_game_over = True
        self.view.show_message("你贏了", f"恭喜你贏得了遊戲！最終得分: {self.model.score}")

    def _handle_lose(self):
        """處理失敗邏輯。"""
        self.model.is_game_over = True
        self.view.show_message("你輸了", "你選了錯誤的格子或清除了答案格子。遊戲結束！")


