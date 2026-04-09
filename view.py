# --- View (Tkinter 介面元件) -----------------------------------------------
import tkinter as tk
from tkinter import messagebox
from model import TileStatus, Tile, SumGame

TILE_SIZE = (50, 50)  # 每個格子的像素大小
FONT = ("Arial", 14)

class GameView:
    """
    View 主類別：負責所有的 Tkinter UI 創建、佈局和管理。
    所有 UI 創建邏輯都在這裡。
    """
    def __init__(self, model: SumGame, controller):
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
        self.tile_views: list[list[TileView]] = []
        self.selected_sum_labels_col: list[SelectedSumLabel] = []  # 上排
        self.selected_sum_labels_row: list[SelectedSumLabel] = []  # 左排
        self.score_label: ScoreLabel|None = None
        
        # 建立所有 UI 元件
        self._build_ui()
        # 綁定點擊事件
        self.canva.bind("<Button-1>", self.on_left_click)
        self.canva.bind("<Button-3>", self.on_right_click)

    def _build_ui(self):
        """建立所有 Tkinter 介面元件並佈局。"""
        x_range, y_range = self.model.x_range, self.model.y_range

        # 主體畫布
        self.canva = tk.Canvas(self.root, width=(x_range+1)*TILE_SIZE[0], height=(y_range+1)*TILE_SIZE[1])
        self.canva.pack()

        # 上排
        for x in range(x_range):
            label = SelectedSumLabel(x, True,
                                    self.canva.create_rectangle(
                                        (x+1)*TILE_SIZE[0], 0,
                                        (x+2)*TILE_SIZE[0], TILE_SIZE[1],
                                        fill="orange", outline="black"),
                                    self.canva.create_text(
                                        (x+1)*TILE_SIZE[0]+TILE_SIZE[0]//2, TILE_SIZE[1]//2, text="0", font=FONT),
                                    self.controller, self.canva)

            self.selected_sum_labels_col.append(label)

        # 左排
        for y in range(y_range):
            label = SelectedSumLabel(y, False,
                                    self.canva.create_rectangle(
                                        0, (y+1)*TILE_SIZE[1],
                                        TILE_SIZE[0], (y+2)*TILE_SIZE[1],
                                        fill="orange", outline="black"),
                                    self.canva.create_text(
                                        TILE_SIZE[0]//2, (y+1)*TILE_SIZE[1]+TILE_SIZE[1]//2, text="0", font=FONT),
                                    self.controller, self.canva)
            self.selected_sum_labels_row.append(label)

        # 中央格子
        for i in range(0, x_range):
            col: list[TileView] = []
            for j in range(0, y_range):
                col.append(
                    TileView(i, j,
                            self.canva.create_rectangle(
                                (i+1)*TILE_SIZE[0], (j+1)*TILE_SIZE[1],
                                (i+2)*TILE_SIZE[0], (j+2)*TILE_SIZE[1],
                                fill="white", outline="black"),
                            self.canva.create_text(
                                (i+1)*TILE_SIZE[0]+TILE_SIZE[0]//2,
                                (j+1)*TILE_SIZE[1]+TILE_SIZE[1]//2,
                                text=f"({i}, {j})", font=FONT),
                            self.canva, self.model))
                
            self.tile_views.append(col)

        # 4. 創建控制面板
        self._build_control_panel(y_range, x_range)

    def _build_control_panel(self, y_range, x_range):
        """建立控制面板（按鈕和分數）。"""
        panel = tk.Frame(self.root)
        panel.pack(pady=10)

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
    
    def on_left_click(self, event: tk.Event) -> None:
        if event.x < TILE_SIZE[0] or event.y < TILE_SIZE[1]: return  # 點擊在標籤區域，不處理
        px, py = event.x//TILE_SIZE[0], event.y//TILE_SIZE[1]
        self.controller.handle_tile_click(px-1, py-1, 'left')

    def on_right_click(self, event: tk.Event) -> None:
        if event.x < TILE_SIZE[0] or event.y < TILE_SIZE[1]: return  # 點擊在標籤區域，不處理
        px, py = event.x//TILE_SIZE[0], event.y//TILE_SIZE[1]
        self.controller.handle_tile_click(px-1, py-1, 'right')

    def mainloop(self) -> None:
        self.root.mainloop()
    
    def destroy(self) -> None:
        self.root.destroy()

    def update_tile_view(self, x: int, y: int) -> None:
        """更新指定座標的格子視圖。"""
        self.tile_views[x][y].update_view()

    def update_all_tiles(self) -> None:
        """更新所有格子視圖。"""
        for x in range(self.model.x_range):
            for y in range(self.model.y_range):
                self.tile_views[x][y].update_view()

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
        messagebox.showinfo(title, message)

    def show_error(self, title, message):
        """顯示錯誤框。"""
        messagebox.showerror(title, message)


class TileView:
    """View 元件：代表遊戲網格中的一個按鈕格子。"""
    def __init__(self, x: int, y: int, rect_id: int, text_id: int, canva: tk.Canvas, model: SumGame) -> None:
        self.x, self.y = x, y
        self.rect_id = rect_id
        self.text_id = text_id
        self.canva = canva
        self.model = model
        
        if model.get_tile(x, y).is_answer:
            self.oval_id = self.canva.create_oval(
                (self.x+1.2)*TILE_SIZE[0], (self.y+1.2)*TILE_SIZE[1],
                (self.x+1.8)*TILE_SIZE[0], (self.y+1.8)*TILE_SIZE[1],
                outline="white", width=2) # 隱藏答案格的圓形標記，初始為白色（不可見）
        
        self.update_view()
    

    def flash(self) -> None:
        """使格子閃爍一段時間以吸引注意。"""
        self.canva.itemconfig(self.rect_id, fill="yellow") # 臨時改變為黃色
        self.canva.after(500, lambda: self.canva.itemconfig(self.rect_id, fill="white"))  # 500ms後恢復原色

    def update_view(self) -> None:
        """根據 Model 的數據更新按鈕的視覺狀態。"""
        tile = self.model.get_tile(self.x, self.y)
        
        self.canva.itemconfig(self.text_id, text=str(tile.number))
        
        if self.model.is_game_over: # 遊戲結束時顯示結果
            self.end_state(tile)
            return

        if tile.status == TileStatus.IS_SELECTED:
            self.canva.itemconfig(self.oval_id, outline="black") # 顯示答案格的圓形標記
        elif tile.status == TileStatus.IS_EXCLUDED: # 已排除
            self.canva.itemconfig(self.rect_id, fill="white")
            self.canva.itemconfig(self.text_id, fill="white") # 隱藏數字
        else: # 初始狀態
            self.canva.itemconfig(self.rect_id, fill="white")
            self.canva.itemconfig(self.text_id, fill="black")
    
    def end_state(self, tile: Tile) -> None:
        if tile.is_answer:
            if tile.status == TileStatus.IS_SELECTED: # 正確選中
                self.canva.itemconfig(self.rect_id, fill="darkgreen")
                self.canva.itemconfig(self.text_id, fill="white")  # 顯示數字
            else: # 應該選中但未選
                self.canva.itemconfig(self.rect_id, fill="yellow")
                self.canva.itemconfig(self.text_id, fill="black")
        else:
            if tile.status == TileStatus.IS_SELECTED: # 錯誤選中
                self.canva.itemconfig(self.rect_id, fill="red")
                self.canva.itemconfig(self.text_id, fill="white")
            else: # 正確忽略
                self.canva.itemconfig(self.rect_id, fill="white")
                self.canva.itemconfig(self.text_id, fill="black")


class SelectedSumLabel:
    """View 元件：顯示應選格子總和與已選格子之和進度"""
    def __init__(self, index: int, is_col: bool, rect_id: int, text_id: int, controller, canva: tk.Canvas) -> None:
        self.index = index
        self.is_col = is_col
        self.rect_id = rect_id
        self.text_id = text_id
        self.controller = controller
        self.canva = canva
        
        self.update_view()

    def update_view(self) -> None:
        """根據 Model 的數據更新標籤的視覺狀態。"""
        target_sum = self.controller.model.calculate_target_sum(self.index, self.is_col)
        current_sum = self.controller.model.calculate_selected_sum(self.index, self.is_col)
        # 顯示格式：目前總和 / 目標總和
        display_text = f"{current_sum}/{target_sum}"
        
        # 顏色邏輯：已選總和 == 目標總和 表示所有答案格子都已選中
        
        bg_color = "green" if current_sum == target_sum else "orange"
        
        self.canva.itemconfig(self.rect_id, fill=bg_color)
        self.canva.itemconfig(self.text_id, text=display_text, fill="white")

class ScoreLabel(tk.Label):
    """View 元件：顯示分數。"""
    def __init__(self, master, controller):
        self.controller = controller
        super().__init__(master=master, text="分數: 0", font=("Arial", 18), bg="pink", fg="gray")
        self.update_view()

    def update_view(self):
        self.config(text=f"分數: {self.controller.model.score}")