# --- View (Tkinter 介面元件) -----------------------------------------------
import tkinter as tk
from model import TileStatus


class GameView:
    """
    View 主類別：負責所有的 Tkinter UI 創建、佈局和管理。
    所有 UI 創建邏輯都在這裡。
    """
    def __init__(self, model, controller):
        """
        初始化遊戲視圖。
        Args:
            model: SumGame 模型實例
            controller: Controller 控制器實例
        """
        self.model = model
        self.controller = controller
        
        # 創建主視窗
        self.root = tk.Tk()
        self.root.title("Sum Game")
        
        # 儲存 View 元件以方便更新
        self.tile_views: list[list[TileView|None]] = [[None for _ in range(model.y_range)] 
                                                   for _ in range(model.x_range)]
        self.selected_sum_labels_col: list[SelectedSumLabel] = []  # 上排
        self.selected_sum_labels_row: list[SelectedSumLabel] = []  # 左排
        self.score_label: ScoreLabel|None = None
        
        # 建立所有 UI 元件
        self._build_ui()

    def _build_ui(self):
        """建立所有 Tkinter 介面元件並佈局。"""
        x_range, y_range = self.model.x_range, self.model.y_range

        # 主體框架
        main_frame = tk.Frame(self.root)
        main_frame.grid(row=1, column=1, columnspan=x_range + 2, rowspan=y_range + 2, padx=10, pady=10)

        # 1. 創建遊戲網格（包含上排/左排）
        board_frame = tk.Frame(main_frame)
        board_frame.grid(row=1, column=1, columnspan=x_range, rowspan=y_range)

        # 讓 grid 容器自適應填滿空間，方便按鈕、標籤尺寸一致
        for col in range(x_range + 2):
            board_frame.grid_columnconfigure(col, weight=1, uniform='grid')
        for row in range(y_range + 2):
            board_frame.grid_rowconfigure(row, weight=1, uniform='grid')

        # 上排
        for x in range(x_range):
            label = SelectedSumLabel(board_frame, self.controller, x, is_col=True)
            label.grid(row=0, column=x + 1, pady=(0, 5), sticky='nsew')
            self.selected_sum_labels_col.append(label)

        # 左排
        for y in range(y_range):
            label = SelectedSumLabel(board_frame, self.controller, y, is_col=False)
            label.grid(row=y + 1, column=0, padx=(0, 5), sticky='nsew')
            self.selected_sum_labels_row.append(label)

        # 中央格子
        for x in range(x_range):
            for y in range(y_range):
                tile_view = TileView(board_frame, x, y, self.controller, self.model)
                self.tile_views[x][y] = tile_view
                tile_view.grid(row=y + 1, column=x + 1, sticky='nsew')  # 放在第1行以上

        # 4. 創建控制面板
        self._build_control_panel(y_range, x_range)

    def _build_control_panel(self, y_range, x_range):
        """建立控制面板（按鈕和分數）。"""
        panel = tk.Frame(self.root)
        panel.grid(row=y_range + 3, column=1, columnspan=x_range, pady=10)

        # 提示按鈕
        prompt_button = tk.Button(
            master=panel, text="提示 (-1 分)", font=("Arial", 18),
            bg="green", fg="white", command=self.controller.handle_prompt
        )
        prompt_button.pack(side=tk.LEFT, padx=10)

        # 分數標籤
        self.score_label = ScoreLabel(panel, self.controller)
        self.score_label.pack(side=tk.LEFT, padx=10)

        # 重新開始按鈕
        restart_button = tk.Button(
            master=panel, text="重新開始", font=("Arial", 18),
            bg="blue", fg="white", command=self.controller.handle_restart
        )
        restart_button.pack(side=tk.LEFT, padx=10)

    def mainloop(self) -> None:
        self.root.mainloop()
    
    def destroy(self) -> None:
        self.root.destroy()

    def update_tile_view(self, x: int, y: int) -> None:
        """更新指定座標的格子視圖。"""
        tile = self.tile_views[x][y]
        assert tile is not None
        tile.update_view()

    def update_all_tiles(self) -> None:
        """更新所有格子視圖。"""
        for x in range(self.model.x_range):
            for y in range(self.model.y_range):
                tile = self.tile_views[x][y]
                assert tile is not None
                tile.update_view()

    def update_selected_sum_labels(self) -> None:
        """更新所有已選和標籤。"""
        for label in self.selected_sum_labels_col + self.selected_sum_labels_row:
            label.update_view()

    def update_score_label(self) -> None:
        """更新分數標籤。"""
        assert self.score_label is not None
        self.score_label.update_view()

    def flash_tile(self, x, y):
        """使指定格子閃爍（用於提示）。"""
        self.tile_views[x][y].flash()

    def show_message(self, title, message):
        """顯示消息框（由 Controller 調用）。"""
        from tkinter import messagebox
        messagebox.showinfo(title, message)

    def show_error(self, title, message):
        """顯示錯誤框。"""
        from tkinter import messagebox
        messagebox.showerror(title, message)


class TileView(tk.Button):
    """View 元件：代表遊戲網格中的一個按鈕格子。"""
    def __init__(self, master: tk.Widget, x: int, y: int, controller, model) -> None:
        self.controller = controller 
        self.model = model
        self.x = x
        self.y = y

        super().__init__(master, width=1, height=1, font=("Arial", 18), bg="white", fg="black")
        
        # 綁定事件
        self.config(command=self.on_click)
        self.bind("<Button-3>", self.right_click)
        
        self.update_view()
    
    def on_click(self):
        self.controller.handle_tile_click(self.x, self.y, 'left')
    def right_click(self, event):
        self.controller.handle_tile_click(self.x, self.y, 'right')

    def flash(self):
        """使格子閃爍一段時間以吸引注意。"""
        original_bg = self.cget("bg")
        self.config(bg="yellow")  # 臨時改變為黃色
        self.after(500, lambda: self.config(bg=original_bg))  # 500ms後恢復原色

    def update_view(self) -> None:
        """根據 Model 的數據更新按鈕的視覺狀態。"""
        tile = self.model.get_tile(self.x, self.y)
        
        self.config(text=str(tile.number), state="normal")
        
        if self.model.is_game_over:
            # 遊戲結束時顯示結果
            if tile.is_answer:
                if tile.status == TileStatus.IS_SELECTED:
                    self.config(bg="darkgreen", fg="white")  # 正確選中
                else:
                    self.config(bg="lightgreen", fg="black")  # 應該選中但未選
            else:
                if tile.status == TileStatus.IS_SELECTED:
                    self.config(bg="darkred", fg="white")  # 錯誤選中
                else:
                    self.config(bg="white", fg="black")  # 正確忽略
            self.config(state="disabled")
            return

        if tile.status == TileStatus.IS_SELECTED:
            self.config(bg="lightgreen" if tile.is_answer else "red", fg="white", state="disabled")
        elif tile.status == TileStatus.IS_EXCLUDED:
            # 已排除/標記
            self.config(text="X", bg="lightgrey", fg="red")
        else:
            # 初始狀態
            self.config(text=str(tile.number), bg="white", fg="black")


class SelectedSumLabel(tk.Label):
    """View 元件：顯示應選格子總和與已選格子之和進度"""
    def __init__(self, master: tk.Widget, controller, index: int, is_col: bool):
        self.controller = controller
        self.index = index
        self.is_col = is_col
        self.target_sum = self.controller.model.calculate_target_sum(index, is_col)
        
        super().__init__(master=master, font=("Arial", 18), bg="orange", fg="black")
        self.update_view()

    def update_view(self) -> None:
        """根據 Model 的數據更新標籤的視覺狀態。"""
        current_sum = self.controller.model.calculate_selected_sum(self.index, self.is_col)
        # 顯示格式：目前總和 / 目標總和
        display_text = f"{current_sum}/{self.target_sum}"
        
        # 顏色邏輯：已選總和 == 目標總和 表示所有答案格子都已選中
        if current_sum == self.target_sum:
            bg_color = "green"
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