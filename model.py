from enum import Enum, auto
import random

# --- Model (遊戲數據與核心邏輯) --------------------------------------------

NUMBER_MIN = 1
NUMBER_MAX = 10

class TileStatus(Enum):
    """格子狀態"""
    NOT_SELECTED = auto() # 未選中
    IS_SELECTED = auto() # 已選中
    IS_EXCLUDED = auto() # 已標記為錯誤格子

class Tile:
    """
    一個格子
    Attributes:
        number (int): 格子的數字
        is_answer (bool): 是否為答案格子
        status (TileStatus): 格子狀態
    """
    __slots__ = ("number", "is_answer", "status")
    def __init__(self) -> None:
        self.number: int = random.randrange(NUMBER_MIN, NUMBER_MAX+1)
        self.is_answer: bool = False
        self.status: TileStatus = TileStatus.NOT_SELECTED
    
    def set_answer(self):
        self.is_answer = True


class SumGame:
    """
    遊戲核心：管理遊戲數據、狀態和核心邏輯。
    Attributes:
        x_range (int): 橫向欄數
        y_range (int): 縱向列數
        score (int): 分數，每選中一個正確格子加一分，使用提示扣一分
        is_game_over (bool): 遊戲是否結束
        grid (list[list[Tile]]): 遊戲格子
        num_correct (int): 正確格子數
        correct_tile_coords (list[tuple[int, int]]): 答案格的 (x, y) 座標
        num_answered (int): 已選中的正確格子數

    """
    def __init__(self, x_range: int, y_range: int, ratio=30):
        self.x_range = x_range
        self.y_range = y_range
        self.score = 0
        self.is_game_over = False

        # 使用列表存儲 Tile 物件
        self.grid = [[Tile() for _ in range(y_range)] for _ in range(x_range)]
        
        self.total_tiles = x_range * y_range
        self.num_correct = self.total_tiles * ratio // 100
        self.correct_tile_coords: list[tuple[int, int]] = []
        self.num_answered = 0

        self._set_answers()

    def _set_answers(self):
        """隨機設置答案格子。"""
        count = 0
        while count < self.num_correct:
            x = random.randint(0, self.x_range - 1)
            y = random.randint(0, self.y_range - 1)
            tile = self.grid[x][y]
            
            if not tile.is_answer:
                tile.set_answer()
                self.correct_tile_coords.append((x, y))
                count += 1
    
    def get_tile(self, x: int, y: int) -> Tile:
        """獲取特定座標的 Tile 物件。"""
        return self.grid[x][y]

    def calculate_target_sum(self, index: int, is_col: bool) -> int:
        """計算一欄或一列中所有答案格子的數字總和 (目標)。
        Attributes:
            index (int): 第幾欄或第幾列
            is_col (bool): 要計算的是否是欄(橫向)
        Returns:
            int: 一欄或一列中所有答案格子的數字總和
        """
        current_sum = 0
        tiles = self.grid[index] if is_col else [self.grid[x][index] for x in range(self.x_range)]
        
        for tile in tiles:
            if tile.is_answer:
                current_sum += tile.number
        return current_sum
    
    def calculate_selected_sum(self, index: int, is_col: bool) -> tuple[int, int, int]:
        """計算一欄或一列中已選答案格子的數字總和 (進度)。
        Attributes:
            index (int): 第幾欄或第幾列
            is_col (bool): 要計算的是否是欄(橫向)
        Returns:
            tuple [int, int, int]:
            答案格子的總數 (num_answer_tiles)
            已選中且是答案格子的總數 (num_selected_tiles)
            已選中且是答案格子的數字總和 (current_sum)
        """
        num_answer_tiles, num_selected_tiles, current_sum = 0, 0, 0
        tiles = self.grid[index] if is_col else [self.grid[x][index] for x in range(self.x_range)]

        for tile in tiles:
            if tile.is_answer:
                num_answer_tiles += 1
                if tile.status == TileStatus.IS_SELECTED:
                    num_selected_tiles += 1
                    current_sum += tile.number
        
        return num_answer_tiles, num_selected_tiles, current_sum
    
    def handle_left_click(self, x: int, y: int) -> bool:
        """處理左鍵點擊邏輯，返回是否導致遊戲失敗。"""
        if self.is_game_over:
            return False

        tile = self.grid[x][y]
        if tile.status != TileStatus.NOT_SELECTED:
            return False # 已經被操作過

        tile.status = TileStatus.IS_SELECTED
        
        if tile.is_answer:
            # 點擊正確答案
            self.num_answered += 1
            self.score += 1
            return False
        else:
            # 點擊錯誤格子 -> 失敗
            self.is_game_over = True
            return True

    def handle_right_click(self, x: int, y: int) -> bool:
        """處理右鍵點擊（清除/標記）邏輯，返回是否導致遊戲失敗。

        Args:
            x (int): 目標格子所在欄索引。
            y (int): 目標格子所在列索引。

        Returns:
            bool: 如果是錯誤操作導致遊戲失敗則為 True，否則為 False。
        """
        if self.is_game_over:
            return False
        
        tile = self.grid[x][y]
        if tile.status == TileStatus.IS_SELECTED:
            return False # 已選中的格子不能清除

        tile.status = TileStatus.IS_EXCLUDED

        if tile.is_answer:
            # 清除答案格子 -> 失敗
            self.is_game_over = True
            return True
        else:
            # 清除非答案格子 -> 成功標記
            return False

    def check_win(self) -> bool:
        """檢查遊戲是否獲勝。"""
        return self.num_answered == self.num_correct

    def use_prompt(self) -> tuple[int, int] | None:
        """使用提示功能，隨機選中一個尚未選中的答案格子。

        Returns:
            tuple[int,int] | None: 被自動選中的格子座標，若無可選則返回 None。
        """
        if self.is_game_over or self.check_win():
            return None # 遊戲結束或已贏，不能使用提示
        
        while True:
            # 隨機選中一個正確格子
            px, py = random.choice(self.correct_tile_coords)
            if self.grid[px][py].status == TileStatus.NOT_SELECTED:
                break
        
        # 強制執行點擊邏輯
        self.grid[px][py].status = TileStatus.IS_SELECTED
        self.num_answered += 1
        self.score -= 1 # 扣分

        return px, py # 返回被提示的座標
