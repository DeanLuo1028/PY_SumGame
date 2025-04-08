import tkinter as tk
import random
from tkinter import messagebox
import numpy as np


class Gezi(tk.Button): # Gezi = 格子
    sumGame = None
    def __init__(s, master, x, y, sumGame):
        super().__init__(master, width=2, height=1, font=("Arial", 20), bg="white", fg="black", state="normal")
        s.x = x
        s.y = y
        s.isAnswer = False
        s.isSelected = False
        s.number = random.randrange(1, 10) # 隨機產生 1 到 9 的數字
        s.config(command=s.selectNumber, text=s.number)
        s.bind("<Button-3>", s.clearNumber)
        s.grid(row=y, column=x)  # 使用 grid 管理格子按钮
        Gezi.sumGame = sumGame

    def setAnswer(s): # 設為答案格子
        if s.isAnswer: return False  # 若格子已設為答案，則返回False表示失敗
        s.isAnswer = True  # 設為答案格子
        Gezi.sumGame.correctGezis.append(s) # 將自己加入正確按鈕組
        return True  # 成功設為答案格子，返回True

    def selectNumber(s):
        if s.isSelected: return False  # 若格子已被選中，則返回False表示失敗
        else:
            s.isSelected = True
            if s.isAnswer:
                s.config(bg="green",fg="white")  # 答案格子顏色改為綠色
                Gezi.sumGame.numOfOperatedIncrease() # 選中答案，已選的正確格子數加 1
                Gezi.sumGame.selected_sum_label[s.x].update(Gezi.sumGame.gezis[s.x ,:]) # 更新下排已選格子之和標題 # 問題出在這
                Gezi.sumGame.selected_sum_label_right[s.y].update(Gezi.sumGame.gezis[:,s.y]) # 更新右排已選格子之和標題 # 問題出在這
                Gezi.sumGame.score_label.plus()
            else:
                s.config(bg="red",fg="white")
                Gezi.sumGame.lose()
            if Gezi.sumGame.isWin(): Gezi.sumGame.win()
            return True  # 成功選中格子，返回True

    def clearNumber(s, event):
        if not s.isSelected:
            s.isSelected = True
            if s.isAnswer:
                s.config(bg="red",fg="white")
                Gezi.sumGame.lose()
            else:
                s.config(text="")
    
    def ISAIA(s): # is Selected and is Answer?
        return s.isSelected and s.isAnswer
                
    def __str__(self):
        return "({},{})".format(self.x, self.y)
    def print(s):
        return str(s)+" "+str(s.number)+" "+str(s.isSelected)+" "+str(s.isAnswer)

class Title(tk.Label): # 正確格子之和
    def __init__(s, master, gezis):
        sum = 0
        for i in range(len(gezis)):
            if gezis[i].isAnswer:
                sum += gezis[i].number

        super().__init__(master=master, text=str(sum), font=("Arial", 20), bg="white", fg="darkblue")

class SelectedTitle(tk.Label): # 已選格子之和
    def __init__(s, master, gezis):
        NOA = 0 # 正確格子數
        for i in range(len(gezis)):
            #print(gezis[i].print())
            if gezis[i].isAnswer:
                NOA += 1
        if NOA == 0:
            super().__init__(master=master, text="0", font=("Arial", 20), bg="green", fg="white")
        else:
            super().__init__(master=master, text="0", font=("Arial", 20), bg="yellow", fg="gray")
    
    def update(s, gezis):
        #print("update")
        NOA, NOS, sum = 0, 0, 0 # 正確格子數、已選格子數、已選格子之和
        for i in range(len(gezis)):
            #print(gezis[i].print())
            if gezis[i].isAnswer:
                NOA += 1
                if gezis[i].isSelected:
                    NOS += 1
                    #print(gezis[i].print())
                    sum += gezis[i].number
        s.config(text=str(sum))
        if NOS == NOA:
            s.config(bg="green", fg="white")


class ScoreLabel(tk.Label):
    score = 0
    def __init__(s, master):
        super().__init__(master=master, text="0", font=("Arial", 20), bg="pink", fg="gray")
    
    def plus(self):
        ScoreLabel.score += 1
        self.config(text=str(ScoreLabel.score))
        self.update()
    
    def minus(self):
        ScoreLabel.score -= 1
        self.config(text=str(ScoreLabel.score))
        self.update()

class SumGame:
    def __init__(s, Xrange, Yrange, ratio=30):
        s.Xrange = Xrange
        s.Yrange = Yrange
        s.ratio = ratio
        s.root = tk.Tk()
        s.root.title("Sum Game")
        s.root.geometry("700x700")
        s.gezis = np.empty((Xrange, Yrange), dtype=object) # 建立二維陣列儲存格子物件
        #s.shangpaitimu = [None for _ in range(Xrange)] # 建立一維陣列儲存上排標題物件
        #s.zuopaitimu = [None for _ in range(Yrange)] # 建立一維陣列儲存左排標題物件
        s.selected_sum_label = [None for _ in range(Xrange)] # 建立一維陣列儲存下排已選格子之和標題物件
        s.selected_sum_label_right = [None for _ in range(Yrange)] # 建立一維陣列儲存右排已選格子之和標題物件
        s.numOfGezi = Xrange * Yrange
        s.numOfOperated = 0 # 已選的正確格子數
        s.numOfCorrectGezi = s.numOfGezi * s.ratio // 100 # ratio% 的格子為答案格
        s.correctGezis = []
        s.prompt_button = None
        s.score_label = None
        s.board = tk.Frame(s.root) # 建立框架
        s.board.grid(row=1, column=1, columnspan=Xrange, rowspan=Yrange) # 使用 grid 放置框架
        s.panel = tk.Frame(s.root)
        s.panel.grid(row=Yrange+2, column=0, columnspan=Xrange)

        for i in range(Xrange):
            for j in range(Yrange):
                s.gezis[i][j] = Gezi(s.board, i, j, s) # 將格子物件存入二維陣列

        s.start() # 開始遊戲
        s.root.mainloop()

    def start(s):
        for _ in range(s.numOfCorrectGezi): # 產生 ratio% 的格子為答案格子
            while True:
                randomX = random.randint(0, s.Xrange - 1)
                randomY = random.randint(0, s.Yrange - 1)
                if not s.gezis[randomX][randomY].setAnswer(): # 若格子已設為答案，則重新產生
                    continue
                break
        # 設定標題
        for i in range(s.Xrange): # 上排標題
            label = Title(s.root, s.gezis[i ,:])
            label.grid(row=0, column=i+1)  # 使用 grid 布局
            #s.shangpaitimu[i] = label
        for i in range(s.Yrange): # 左排標題
            label = Title(s.root, s.gezis[:, i])
            label.grid(row=i+1, column=0)  # 使用 grid 布局
        
        # 設定已選格子之和標題
        for i in range(s.Xrange): # 下排標題
            label = SelectedTitle(s.root, s.gezis[i ,:])
            label.grid(row=s.Yrange+1, column=i+1)  # 使用 grid 布局
            s.selected_sum_label[i] = label
        for i in range(s.Yrange): # 右排標題
            label = SelectedTitle(s.root, s.gezis[:, i])
            label.grid(row=i+1, column=s.Xrange+1)  # 使用 grid 布局
            s.selected_sum_label_right[i] = label

        s.prompt_button = tk.Button(master=s.panel, text="提示", font=("Arial", 20), bg="green", fg="white", command=s.prompt)
        s.prompt_button.pack()
        s.score_label = ScoreLabel(s.panel)
        s.score_label.pack()
        '''
        for j in range(s.Xrange):
            for i in range(s.Yrange):
                print(s.gezis[i][j].print(), end=", ")
            print()'''
    
    def numOfOperatedIncrease(s):
        s.numOfOperated += 1
        print("已選格子數:", s.numOfOperated)
    
    def isWin(s): # 獲勝條件為選完所有答案格子並清除所有非答案格子
        return s.numOfOperated == s.numOfCorrectGezi
    
    def win(s): # 獲勝條件為選完所有答案格子並清除所有非答案格子
        print("已選格子數:", s.numOfOperated)
        messagebox.showinfo("你贏了","恭喜你贏得了這個遊戲！")
    
    def lose(s):
        print("已選格子數:", s.numOfOperated)
        for i in range(s.Xrange):
            for j in range(s.Yrange):
                s.gezis[i][j].isSelected = True # 將所有格子設為已選
        messagebox.showinfo("你輸了","你選了不該選的格子或清除了不該清除的格子")
        
    def prompt(s): # 提示
        s.score_label.minus()
        if s.isWin(): return
        while True:
            gezi = random.choice(s.correctGezis)
            if gezi.selectNumber(): return
            else: continue
        

def start(text_x, text_y, text_ratio):
    try:
        x = int(text_x)
        y = int(text_y)
        if text_ratio == "": ratio = 30
        else: ratio = int(text_ratio)
        if ratio <= 0 or ratio > 100:
            messagebox.showinfo("錯誤！", "答案格比例請輸入 1 到 100 的整數！")
            return
        if x <= 0 or y <= 0:
            messagebox.showinfo("錯誤！", "請輸入正確的數字！")
            return
        #root.destroy()
        SumGame(x, y, ratio)
        
    except Exception as e:
        messagebox.showerror("錯誤！", e)
        return

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Sum Game 遊戲設定")
    root.geometry("400x300")
    word_label = tk.Label(master=root, text="請輸入大小")
    word_label.grid(row=0, column=0, columnspan=2)
    word_x_label = tk.Label(master=root, text="請輸入x:")
    word_x_label.grid(row=1, column=0)
    entry_x = tk.Entry(master=root)
    entry_x.grid(row=1, column=1)
    word_y_label = tk.Label(master=root, text="請輸入y:")
    word_y_label.grid(row=2, column=0)
    entry_y = tk.Entry(master=root)
    entry_y.grid(row=2, column=1)
    word_ratio_label = tk.Label(master=root, text="請輸入答案格比例(%):")
    word_ratio_label.grid(row=3, column=0)
    entry_ratio = tk.Entry(master=root)
    entry_ratio.grid(row=3, column=1)
    button = tk.Button(master=root, text="開始遊戲！", command=lambda: start(entry_x.get(), entry_y.get(), entry_ratio.get()))
    button.grid(row=4, column=1, rowspan=2)
    root.mainloop()
    #只是測試
    #成功了!
