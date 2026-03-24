import tkinter as tk
from tkinter import messagebox
import random

# --- 1. Model (遊戲數據與核心邏輯) --------------------------------------------

class SumGameModel:
    """
    遊戲模型：管理遊戲數據、狀態和核心邏輯。
    不包含任何 GUI 相關的程式碼。
    """
    def __init__(self, x_range, y_range, ratio=30):
        self.Xrange = x_range
        self.Yrange = y_range
        self.ratio = ratio
        self.score = 0
        self.is_game_over = False

        # 使用列表存儲數據
        self.grid = [[{'number': random.randrange(1, 10),
                       'is_answer': False,
                       'is_selected': False,  # True: 玩家已選中 (LMB)
                       'is_excluded': False} # True: 玩家已清除 (RMB)
                       for _ in range(y_range)] for _ in range(x_range)]
        
        self.total_tiles = x_range * y_range
        self.num_correct_to_set = self.total_tiles * self.ratio // 100
        self.correct_tile_coords = [] # 儲存答案格的 (x, y) 座標
        self.num_operated = 0       # 已選中的正確格子數

        self._set_answers()

    def _set_answers(self):
        """隨機設置答案格子。"""
        count = 0
        while count < self.num_correct_to_set:
            x = random.randint(0, self.Xrange - 1)
            y = random.randint(0, self.Yrange - 1)
            tile_data = self.grid[x][y]
            
            if not tile_data['is_answer']:
                tile_data['is_answer'] = True
                self.correct_tile_coords.append((x, y))
                count += 1
    
    def get_tile_data(self, x, y):
        """獲取特定座標的格子數據字典。"""
        return self.grid[x][y]

    def calculate_target_sum(self, index, is_col):
        """計算一行或一列中所有答案格子的數字總和 (目標和)。"""
        current_sum = 0
        tiles = self.grid[index] if is_col else [self.grid[x][index] for x in range(self.Xrange)]
        
        for tile in tiles:
            if tile['is_answer']:
                current_sum += tile['number']
        return current_sum
    
    def calculate_selected_sum(self, index, is_col):
        """
        計算一行或一列中：
        1. 答案格子的總數 (answer_tiles_num)
        2. 已選中且是答案格子的總數 (selected_tiles_num)
        3. 已選中且是答案格子的數字總和 (sum)
        """
        answer_tiles_num, selected_tiles_num, current_sum = 0, 0, 0
        tiles = self.grid[index] if is_col else [self.grid[x][index] for x in range(self.Xrange)]

        for tile in tiles:
            if tile['is_answer']:
                answer_tiles_num += 1
                if tile['is_selected']:
                    selected_tiles_num += 1
                    current_sum += tile['number']
        
        return answer_tiles_num, selected_tiles_num, current_sum
    
    def handle_left_click(self, x: int, y:int):
        """處理左鍵點擊邏輯，返回是否導致遊戲失敗。"""
        if self.is_game_over: return False

        tile_data = self.grid[x][y]
        if tile_data['is_selected'] or tile_data['is_excluded']:
            return False # 已經被操作過

        tile_data['is_selected'] = True
        
        if tile_data['is_answer']:
            # 點擊正確答案
            self.num_operated += 1
            self.score += 1
            return False
        else:
            # 點擊錯誤格子 -> 失敗
            self.is_game_over = True
            return True

    def handle_right_click(self, x, y):
        """處理右鍵點擊（清除/標記）邏輯，返回是否導致遊戲失敗。"""
        if self.is_game_over: return False
        
        tile_data = self.grid[x][y]
        if tile_data['is_selected']:
            return False # 已選中的格子不能清除

        tile_data['is_excluded'] = True

        if tile_data['is_answer']:
            # 清除答案格子 -> 失敗
            self.is_game_over = True
            return True
        else:
            # 清除非答案格子 -> 成功標記
            return False

    def check_win(self):
        """檢查遊戲是否獲勝。"""
        return self.num_operated == self.num_correct_to_set

    def use_prompt(self):
        """使用提示功能，隨機選中一個尚未選中的答案格子。"""
        if self.is_game_over or self.check_win():
            return None # 遊戲結束或已贏，不能使用提示
        
        # 尋找所有未選中的答案格
        unselected_answers = [(x, y) for x, y in self.correct_tile_coords
                              if not self.grid[x][y]['is_selected']]
        
        if not unselected_answers:
            return None

        # 隨機選中一個
        px, py = random.choice(unselected_answers)
        
        # 強制執行點擊邏輯
        self.grid[px][py]['is_selected'] = True
        self.num_operated += 1
        self.score -= 1 # 扣分

        return px, py # 返回被提示的座標
