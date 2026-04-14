# --- View (Tkinter 介面元件) -----------------------------------------------
import tkinter as tk
from tkinter import messagebox
from model import TileStatus, Tile, SumGame
from Color import *

TILE_SIZE = (50, 50)  # 每個格子的像素大小
FONT = ("Arial", 14)
LITTLE_FONT = ("Arial", 10)

class View:
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
        self.group_sum_labels: list[GroupSumLabel] = []  # 組總和標籤
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
                                        fill=WHITE, outline=BLACK),
                                    self.canva.create_text(
                                        (x+1)*TILE_SIZE[0]+TILE_SIZE[0]//2, TILE_SIZE[1]//2,
                                        text="-1", font=FONT, fill=BLACK),
                                    self.model, self.canva)

            self.selected_sum_labels_col.append(label)

        # 左排
        for y in range(y_range):
            label = SelectedSumLabel(y, False,
                                    self.canva.create_rectangle(
                                        0, (y+1)*TILE_SIZE[1],
                                        TILE_SIZE[0], (y+2)*TILE_SIZE[1],
                                        fill=WHITE, outline=BLACK),
                                    self.canva.create_text(
                                        TILE_SIZE[0]//2, (y+1)*TILE_SIZE[1]+TILE_SIZE[1]//2,
                                        text="-1", font=FONT, fill=BLACK),
                                    self.model, self.canva)
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
                                fill=WHITE, outline=BLACK),
                            self.canva.create_text(
                                (i+1)*TILE_SIZE[0]+TILE_SIZE[0]//2,
                                (j+1)*TILE_SIZE[1]+TILE_SIZE[1]//2,
                                text=f"({i}, {j})", font=FONT),
                            self.canva, self.model))
                
            self.tile_views.append(col)

        # 組總和標籤
        for seed in self.model.seeds:
            label = GroupSumLabel(seed[2], self.canva.create_text(
                (seed[0] + 1) * TILE_SIZE[0] + 5,
                (seed[1] + 1) * TILE_SIZE[1] + 5,
                text="-1", font=LITTLE_FONT, anchor="nw"),
                self.model, self.canva)
            self.group_sum_labels.append(label)

        # 4. 創建控制面板
        self._build_control_panel()

    def _build_control_panel(self):
        """建立控制面板（按鈕和分數）。"""
        panel = tk.Frame(self.root)
        panel.pack(pady=10)

        # 提示按鈕
        prompt_button = tk.Button(
            master=panel, text="提示 (-1 分)", font=("Arial", 18),
            bg=GREEN, fg=WHITE, command=self.controller.handle_prompt
        )
        prompt_button.pack(side=tk.LEFT, padx=10)

        # 分數標籤
        self.score_label = ScoreLabel(panel, self.model)
        self.score_label.pack(side=tk.LEFT, padx=10)

        # 重新開始按鈕
        restart_button = tk.Button(
            master=panel, text="重新開始", font=("Arial", 18),
            bg=BLUE, fg=WHITE, command=self.controller.handle_restart
        )
        restart_button.pack(side=tk.LEFT, padx=10)
    
    def on_left_click(self, event: tk.Event) -> None:
        px, py = event.x//TILE_SIZE[0], event.y//TILE_SIZE[1]
        self.controller.handle_tile_click(px-1, py-1, 'left')

    def on_right_click(self, event: tk.Event) -> None:
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
    
    def update_selected_sum_label(self, x: int, y: int) -> None:
        """更新該格子所在欄和列的已選總和標籤。"""
        self.selected_sum_labels_col[x].update_view()
        self.selected_sum_labels_row[y].update_view()
    
    def update_all_selected_sum_labels(self) -> None:
        """更新所有已選和標籤。"""
        for label in self.selected_sum_labels_col + self.selected_sum_labels_row:
            label.update_view()

    def update_group_sum_label(self, group_id: int) -> None:
        """更新指定組的總和標籤。"""
        self.group_sum_labels[group_id].update_view()

    def update_all_group_sum_label(self) -> None:
        """更新所有組總和標籤。"""
        for label in self.group_sum_labels:
            label.update_view()

    def update_score_label(self) -> None:
        """更新分數標籤。"""
        assert self.score_label is not None
        self.score_label.update_view()

    def flash_tile(self, x, y):
        """使指定格子閃爍（用於提示）。"""
        self.tile_views[x][y].flash()

    def show_message(self, title, message):
        """顯示消息框"""
        messagebox.showinfo(title, message)

    def show_error(self, title, message):
        """顯示錯誤框。"""
        messagebox.showerror(title, message)


class TileView:
    """View 元件：代表遊戲網格中的一個按鈕格子。"""
    __slots__ = ('x', 'y', 'rect_id', 'text_id', 'canva', 'model', 'oval_id')
    
    def __init__(self, x: int, y: int, rect_id: int, text_id: int, canva: tk.Canvas, model: SumGame) -> None:
        self.x, self.y = x, y
        self.rect_id = rect_id
        self.text_id = text_id
        self.canva = canva
        self.model = model
        
        color = self.model.get_tile_color(self.x, self.y)
        # 圓形表示格子被選中
        self.oval_id = self.canva.create_oval(
            (self.x+1.2)*TILE_SIZE[0], (self.y+1.2)*TILE_SIZE[1],
            (self.x+1.8)*TILE_SIZE[0], (self.y+1.8)*TILE_SIZE[1],
            outline=color, width=2) # 隱藏選中的圓形標記，初始為與格子同色(不可見)
        
        self.update_view()

    def flash(self) -> None:
        """使格子閃爍一段時間以吸引注意。"""
        color = self.model.get_tile_color(self.x, self.y)
        if color == YELLOW:
            self.canva.itemconfig(self.rect_id, fill=WHITE) # 臨時改變成白色
        else:
            self.canva.itemconfig(self.rect_id, fill=YELLOW) # 臨時改變成黃色
        self.canva.itemconfig(self.text_id, fill=BLACK) # 顯示數字
        def restore_color():
            self.canva.itemconfig(self.rect_id, fill=color) # 恢復原色
            self.canva.itemconfig(self.text_id, fill=WHITE if color in DARK else BLACK) # 根據背景顏色調整文字顏色
        self.canva.after(500, restore_color) # 500ms後恢復原色

    def update_view(self) -> None:
        """根據 Model 的數據更新按鈕的視覺狀態。"""
        tile = self.model.get_tile(self.x, self.y)
        
        self.canva.itemconfig(self.text_id, text=str(tile.number))
        
        if self.model.is_game_over: # 遊戲結束時顯示結果
            self.end_state(tile)
            return

        color = self.model.get_tile_color(self.x, self.y)
        if tile.status == TileStatus.IS_EXCLUDED: # 已排除
            self.canva.itemconfig(self.rect_id, fill=color)
            self.canva.itemconfig(self.text_id, fill=color) # 隱藏數字
        else:
            self.canva.itemconfig(self.rect_id, fill=color)
            self.canva.itemconfig(self.text_id, fill=WHITE if color in DARK else BLACK) # 根據背景顏色調整文字顏色
            if tile.status == TileStatus.IS_SELECTED:
                self.canva.itemconfig(self.oval_id, outline=WHITE if color in DARK else BLACK) # 顯示答案格的圓形標記
            else:
                self.canva.itemconfig(self.oval_id, outline=color) # 隱藏答案格的圓形標記
    
    def end_state(self, tile: Tile) -> None:
        if tile.is_answer:
            if tile.status == TileStatus.IS_SELECTED: # 正確選中
                self.canva.itemconfig(self.rect_id, fill=GREEN)
                self.canva.itemconfig(self.text_id, fill=WHITE)  # 顯示數字
                self.canva.itemconfig(self.oval_id, outline=WHITE) # 顯示正確選中的圓形標記
            else: # 應該選中但未選
                self.canva.itemconfig(self.rect_id, fill=YELLOW)
                self.canva.itemconfig(self.text_id, fill=BLACK)
                self.canva.itemconfig(self.oval_id, outline=YELLOW) # 未選中所以隱藏圓形標記，但用黃色框出來表示遺漏了這個答案格
        else:
            if tile.status == TileStatus.IS_SELECTED: # 錯誤選中
                self.canva.itemconfig(self.rect_id, fill=RED)
                self.canva.itemconfig(self.text_id, fill=WHITE)
                self.canva.itemconfig(self.oval_id, outline=YELLOW, width=2, dash=(5, 5)) # 顯示錯誤選中的圓形標記
            else: # 正確忽略
                self.canva.itemconfig(self.rect_id, fill=WHITE)
                self.canva.itemconfig(self.text_id, fill=BLACK)
                self.canva.itemconfig(self.oval_id, outline=WHITE) # 隱藏圓形標記


class SelectedSumLabel:
    """View 元件：顯示應選格子總和與已選格子之和進度"""
    __slots__ = ('index', 'is_col', 'rect_id', 'text_id', 'model', 'canva')
    
    def __init__(self, index: int, is_col: bool, rect_id: int, text_id: int, model: SumGame, canva: tk.Canvas) -> None:
        self.index = index
        self.is_col = is_col
        self.rect_id = rect_id
        self.text_id = text_id
        self.model = model
        self.canva = canva
        
        self.update_view()

    def update_view(self) -> None:
        """根據 Model 的數據更新標籤的視覺狀態。"""
        target_sum = self.model.calculate_target_sum(self.index, self.is_col)
        current_sum = self.model.calculate_selected_sum(self.index, self.is_col)
        # 顯示格式：目前總和 / 目標總和
        display_text = f"{current_sum}/{target_sum}"
        
        # 顏色邏輯：已選總和 == 目標總和 表示所有答案格子都已選中
        
        bg_color = GREEN if current_sum == target_sum else WHITE
        
        self.canva.itemconfig(self.rect_id, fill=bg_color)
        self.canva.itemconfig(self.text_id, text=display_text, fill=WHITE if bg_color == GREEN else BLACK)


class GroupSumLabel:
    """View 元件：顯示每個組的總和。"""
    __slots__ = ('group_id', 'text_id', 'model', 'canva')
    
    def __init__(self, group_id: int, text_id: int, model: SumGame, canva: tk.Canvas) -> None:
        self.group_id = group_id
        self.text_id = text_id
        self.model = model
        self.canva = canva
        
        self.update_view()

    def update_view(self) -> None:
        """根據 Model 的數據更新標籤的視覺狀態。"""
        group_sum = self.model.calculate_group_target_sum(self.group_id)
        current_sum = self.model.calculate_group_selected_sum(self.group_id)
        display_text = f"{current_sum}/{group_sum}"
        
        if self.model.groups_color[self.group_id] in DARK:
            text_color = WHITE
        else:
            text_color = BLACK
        self.canva.itemconfig(self.text_id, text=display_text, fill=text_color)


class ScoreLabel(tk.Label):
    """View 元件：顯示分數。"""
    __slots__ = ('model',)
    
    def __init__(self, master, model: SumGame):
        self.model = model
        super().__init__(master=master, text="分數: 0", font=("Arial", 18), bg="pink", fg="gray")
        self.update_view()

    def update_view(self):
        self.config(text=f"分數: {self.model.score}")