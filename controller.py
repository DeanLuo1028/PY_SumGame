# --- Controller (協調 Model 和 View) -----------------------------------------------
from model import SumGame
from view import View


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
        self.view = View(self.model, self)
        
        self.mainloop()
    
    def mainloop(self):
        """遊戲主事件循環，處理遊戲過程中的所有事件和更新。"""
        try:
            self.view.mainloop()
        except KeyboardInterrupt:
            self.view.show_message("遊戲中斷", "遊戲已被中斷。")
            self.view.destroy()
        except Exception as e:
            self.view.show_message("錯誤！", f"遊戲發生未知錯誤: {e}")
            # 這裡不 self.view.destroy() 是為了保留視窗以方便除錯

    # --- 更新 View 方法 ---
    
    def _update_all_views(self) -> None:
        """通知所有相關 View 刷新顯示。"""
        self.view.update_all_tiles()
        self.view.update_all_selected_sum_labels()
        self.view.update_all_group_sum_label()
        self.view.update_score_label()
    
    def _update_one_tileview(self, x: int, y: int) -> None:
        """更新特定格子相關的 View 顯示。

        Args:
            x (int): 格子欄索引。
            y (int): 格子列索引。
        """
        self.view.update_tile_view(x, y) # 只更新被點擊的格子
        self.view.update_selected_sum_label(x, y) # 更新被點擊格子的選擇和標籤數字顯示
        self.view.update_group_sum_label(self.model.get_tile(x, y).group_id) # 更新被點擊格子所在組的總和標籤顯示
        self.view.update_score_label()
    
    # --- 事件處理方法 ---

    def handle_tile_click(self, x: int, y: int, button_type: str) -> None:
        """處理格子點擊事件。

        Args:
            x (int): 被點擊格子的欄索引。
            y (int): 被點擊格子的列索引。
            button_type (str): 按鍵類型，'left' 或 'right'。
        """
        if not self.model.check_range(x, y): return
        
        is_fail = False
        
        if button_type == 'left':
            is_fail = self.model.handle_left_click(x, y)
        elif button_type == 'right':
            is_fail = self.model.handle_right_click(x, y)
        
        self._update_one_tileview(x, y) # 只更新被點擊的格子和相關資訊，提升效率
        
        if is_fail:
            self._handle_lose()
            return
        
        # 檢查勝利
        if self.model.check_win():
            self._handle_win()

    def handle_prompt(self) -> None:
        """處理提示按鈕點擊事件。"""
        prompt_coords = self.model.use_prompt()
        if prompt_coords:
            self._update_one_tileview(*prompt_coords) # 只更新提示的格子和相關資訊，提升效率
            if self.model.check_win():
                self._handle_win()
                return
            self.view.flash_tile(*prompt_coords)
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
        self._update_all_views() # 確保所有格子和標籤都更新到最新狀態
        self.view.show_message("你贏了", f"恭喜你贏得了遊戲！最終得分: {self.model.score}")

    def _handle_lose(self):
        """處理失敗邏輯。"""
        self.model.is_game_over = True
        self._update_all_views() # 確保所有格子和標籤都更新到最新狀態
        self.view.show_message("你輸了", "你選了錯誤的格子或清除了答案格子。遊戲結束！")


