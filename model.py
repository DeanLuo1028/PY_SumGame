from enum import Enum, auto
import random
from Color import COLORS

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
        group_id (int): 分組 ID，用於顏色分組
    """
    __slots__ = ("number", "is_answer", "status", "group_id")
    def __init__(self) -> None:
        self.number: int = random.randint(NUMBER_MIN, NUMBER_MAX)
        self.is_answer: bool = False
        self.status: TileStatus = TileStatus.NOT_SELECTED
        self.group_id: int = -1 # 分組 ID，初始化為 -1 表示未分組
    
    def set_answer(self) -> None:
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
        num_group (int): 分組數量
        groups_color (list[str]): 每個分組對應的顏色列表

    """
    def __init__(self, x_range: int, y_range: int, ratio=30) -> None:
        self.x_range = x_range
        self.y_range = y_range
        self.score = 0
        self.is_game_over = False

        # 使用列表存儲 Tile 物件
        self.grid = [[Tile() for _ in range(y_range)] for _ in range(x_range)]
        
        self.total_tiles = x_range * y_range
        self.num_correct = max(1, self.total_tiles * ratio // 100) # 至少一個答案格
        self.correct_tile_coords: list[tuple[int, int]] = []
        self.num_answered = 0
        
        self.num_group = (x_range + y_range) // 2
        self.groups_color = random.sample(COLORS, self.num_group)
        self.groups: list[list[Tile]] = [[] for _ in range(self.num_group)] # 每個組的格子列表，初始化為 None
        self._set_answers()
        self.group_all_tiles()

    def _set_answers(self) -> None:
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
    
    def check_range(self, x: int, y: int) -> bool:
        return 0 <= x < self.x_range and 0 <= y < self.y_range
    
    def group_all_tiles(self) -> None:
        """將所有格子分組

        使用改進的洪水填充算法創建高度連續的組。
        確保每個組的格子在空間上是連續的，相鄰格子屬於同組。
        """
        from collections import deque

        # 將網格分成幾個區域，每個區域作為一個組的種子區域
        seeds: list[tuple[int, int]] = []
        # 計算網格分割
        cols = max(1, int(self.num_group ** 0.5))
        rows = (self.num_group + cols - 1) // cols

        for i in range(self.num_group):
            # 計算這個組在分割網格中的位置
            grid_x = i % cols
            grid_y = i // cols

            # 計算這個區域的中心點
            region_width = self.x_range // cols
            region_height = self.y_range // rows

            start_x = grid_x * region_width
            start_y = grid_y * region_height

            # 區域中心
            center_x = start_x + region_width // 2
            center_y = start_y + region_height // 2

            # 確保在邊界內
            center_x = max(0, min(center_x, self.x_range - 1))
            center_y = max(0, min(center_y, self.y_range - 1))
            
            seeds.append((center_x, center_y))

        # 初始化種子位置的組 id
        for group_id, (sx, sy) in enumerate(seeds):
            self.grid[sx][sy].group_id = group_id

        # 使用競爭性填充：所有組同時擴展
        queues = [deque([seed]) for seed in seeds]
        group_sizes = [1] * self.num_group  # 種子已經算作1
        DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        # 競爭性填充過程 - 限制迭代次數避免無限循環
        max_iterations = self.total_tiles * 2  # 安全上限
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            expanded_any = False
            
            for group_id in range(self.num_group):
                if not queues[group_id]:
                    continue

                # 限制組的大小
                max_size = self.total_tiles // self.num_group + 2
                if group_sizes[group_id] >= max_size:
                    # 清空隊列避免卡住
                    queues[group_id].clear()
                    continue

                # 從隊列中取一個位置
                x, y = queues[group_id].popleft()

                # 嘗試擴展到一個隨機相鄰格子
                neighbors = []
                for dx, dy in DIRECTIONS:
                    nx, ny = x + dx, y + dy
                    if (self.check_range(nx, ny)
                    and self.grid[nx][ny].group_id == -1):
                        neighbors.append((nx, ny))

                if neighbors:
                    # 隨機選擇一個相鄰格子
                    nx, ny = random.choice(neighbors)
                    self.grid[nx][ny].group_id = group_id
                    queues[group_id].append((nx, ny))
                    group_sizes[group_id] += 1
                    expanded_any = True
            
            # 如果沒有任何擴展，停止
            if not expanded_any:
                break

        # 最終檢查：確保沒有未分組的格子
        for x in range(self.x_range):
            for y in range(self.y_range):
                if self.grid[x][y].group_id == -1:
                    # 找到最近的組
                    min_distance = float('inf')
                    closest_group = 0
                    for gx in range(self.x_range):
                        for gy in range(self.y_range):
                            if self.grid[gx][gy].group_id != -1:
                                dist = abs(x - gx) + abs(y - gy)
                                if dist < min_distance:
                                    min_distance = dist
                                    closest_group = self.grid[gx][gy].group_id
                    self.grid[x][y].group_id = closest_group
        
        for x in range(self.x_range):
            for y in range(self.y_range):
                group_id = self.grid[x][y].group_id
                self.groups[group_id].append(self.grid[x][y])
        # 儲存種子位置以供 View 使用
        self.seeds = []
        for seed in seeds:
            self.seeds.append((*seed, self.grid[seed[0]][seed[1]].group_id))

    def get_tile_color(self, x: int, y: int) -> str:
        """根據格子的 group_id 返回對應的顏色。"""
        tile = self.grid[x][y]
        if tile.group_id != -1:
            return self.groups_color[tile.group_id]
        return "white" # 預設顏色
    
    def get_tile(self, x: int, y: int) -> Tile:
        return self.grid[x][y]
    
    def calculate_target_sum(self, index: int, is_col: bool) -> int:
        """計算一欄或一列中所有答案格子的數字總和 (目標)。
        Attributes:
            index (int): 第幾欄或第幾列
            is_col (bool): 要計算的是否是欄(橫向)
        Returns:
            int: 一欄或一列中所有答案格子的數字總和
        """
        if is_col:
            return sum(tile.number
                       for tile in self.grid[index]
                       if tile.is_answer)
        else:
            return sum(tile.number
                       for tile in [self.grid[x][index] for x in range(self.x_range)]
                       if tile.is_answer)
    
    def calculate_selected_sum(self, index: int, is_col: bool) -> int:
        """計算一欄或一列中已選答案格子的數字總和 (進度)。
        Attributes:
            index (int): 第幾欄或第幾列
            is_col (bool): 要計算的是否是欄(橫向)
        Returns:
            int: 已選中且是答案格子的數字總和 (current_sum)
        """
        if is_col:
            return sum(tile.number
                       for tile in self.grid[index]
                       if tile.is_answer and tile.status == TileStatus.IS_SELECTED)
        else:
            return sum(tile.number
                       for tile in [self.grid[x][index] for x in range(self.x_range)]
                       if tile.is_answer and tile.status == TileStatus.IS_SELECTED)
    
    def calculate_group_target_sum(self, group_id: int) -> int:
        """計算一個組內所有正確格子的數字總和。"""
        return sum(tile.number
                   for tile in self.groups[group_id]
                   if tile.is_answer)
    
    def calculate_group_selected_sum(self, group_id: int) -> int:
        """計算一個組內已選中正確格子的數字總和。"""
        return sum(tile.number
                   for tile in self.groups[group_id]
                   if tile.is_answer and tile.status == TileStatus.IS_SELECTED)

    def handle_left_click(self, x: int, y: int) -> bool:
        """處理左鍵點擊邏輯，返回是否導致遊戲失敗。"""
        if self.is_game_over:
            return False
        if x < 0 or x >= self.x_range or y < 0 or y >= self.y_range:
            return False # 無效座標

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
        if x < 0 or x >= self.x_range or y < 0 or y >= self.y_range:
            return False # 無效座標
        
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
