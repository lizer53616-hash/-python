import tkinter as tk
from random import shuffle
from tkinter.messagebox import showinfo, showerror
import json
import os

class GameConfig:
    """Класс для хранения конфигурации игры"""
    def __init__(self):
        self.ROW = 7
        self.COLUMNS = 10
        self.MINES = 10
        self.COLORS = {
            0: 'white',
            1: '#ff0000',
            2: '#00ff00',
            3: '#0000ff',
            4: '#ffff00',
            5: '#ff00ff',
            6: '#00ffff',
            7: '#800000',
            8: '#808000'
        }
    
    def save_to_file(self, filename='data/settings.json'):
        """Сохранить настройки в файл"""
        data = {
            'rows': self.ROW,
            'columns': self.COLUMNS,
            'mines': self.MINES
        }
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(data, f)
    
    def load_from_file(self, filename='data/settings.json'):
        """Загрузить настройки из файла"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                self.ROW = data.get('rows', 7)
                self.COLUMNS = data.get('columns', 10)
                self.MINES = data.get('mines', 10)
        except FileNotFoundError:
            self.save_to_file(filename)

class MyButton(tk.Button):
    """Кастомная кнопка для игры Сапер"""
    def __init__(self, master, x, y, number=0, *args, **kwargs):
        super().__init__(master, width=3, font='Arial 15 bold', *args, **kwargs)
        self.x = x
        self.y = y
        self.number = number
        self.is_mine = False
        self.count_bomb = 0
        self.is_open = False
        self.is_flagged = False

class MineSweeper:
    """Основной класс игры Сапер"""
    
    def __init__(self):
        self.config = GameConfig()
        self.config.load_from_file()
        
        self.window = tk.Tk()
        self.window.title("Сапер")
        self.window.geometry("500x400")
        
        self.is_game_over = False
        self.is_first_click = True
        self.flags_placed = 0
        
        self.timer_running = False
        self.seconds = 0
        self.timer_label = None
        
        self.create_widgets()
    
    def create_widgets(self):
        """Создание интерфейса игры"""
        # Панель управления
        control_frame = tk.Frame(self.window, bg='lightgray', height=50)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        # Таймер
        self.timer_label = tk.Label(control_frame, text="Время: 00:00", 
                                    font='Arial 12 bold', bg='lightgray')
        self.timer_label.pack(side='left', padx=10)
        
        # Счетчик мин
        self.mine_counter = tk.Label(control_frame, 
                                    text=f"Мины: {self.config.MINES}/{self.config.MINES}",
                                    font='Arial 12 bold', bg='lightgray')
        self.mine_counter.pack(side='right', padx=10)
        
        # Кнопка перезапуска
        restart_btn = tk.Button(control_frame, text="🔄", 
                               font='Arial 14', command=self.restart_game)
        restart_btn.pack(side='top', pady=5)
        
        # Игровое поле
        self.game_frame = tk.Frame(self.window)
        self.game_frame.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Создание меню
        self.create_menu()
        
        # Инициализация кнопок
        self.buttons = []
        self.create_buttons()
    
    def create_menu(self):
        """Создание меню"""
        menubar = tk.Menu(self.window)
        self.window.config(menu=menubar)
        
        # Меню "Игра"
        game_menu = tk.Menu(menubar, tearoff=0)
        game_menu.add_command(label="Новая игра", command=self.restart_game)
        game_menu.add_separator()
        game_menu.add_command(label="Настройки", command=self.open_settings)
        game_menu.add_separator()
        game_menu.add_command(label="Выход", command=self.window.quit)
        menubar.add_cascade(label="Игра", menu=game_menu)
        
        # Меню "Справка"
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Правила", command=self.show_rules)
        help_menu.add_command(label="О программе", command=self.show_about)
        menubar.add_cascade(label="Справка", menu=help_menu)
    
    def create_buttons(self):
        """Создание игрового поля"""
        # Очистка предыдущих кнопок
        for widget in self.game_frame.winfo_children():
            widget.destroy()
        
        self.buttons = []
        for i in range(self.config.ROW + 2):
            temp = []
            for j in range(self.config.COLUMNS + 2):
                btn = MyButton(self.game_frame, x=i, y=j)
                btn.config(command=lambda button=btn: self.click(button))
                btn.bind('<Button-3>', self.right_click)
                temp.append(btn)
            self.buttons.append(temp)
        
        # Размещение кнопок на сетке
        count = 1
        for i in range(1, self.config.ROW + 1):
            for j in range(1, self.config.COLUMNS + 1):
                btn = self.buttons[i][j]
                btn.number = count
                btn.grid(row=i, column=j, sticky='nsew')
                count += 1
        
        # Настройка весов сетки
        for i in range(1, self.config.ROW + 1):
            tk.Grid.rowconfigure(self.game_frame, i, weight=1)
        
        for i in range(1, self.config.COLUMNS + 1):
            tk.Grid.columnconfigure(self.game_frame, i, weight=1)
    
    def start_timer(self):
        """Запуск таймера"""
        if not self.timer_running:
            self.timer_running = True
            self.update_timer()
    
    def update_timer(self):
        """Обновление таймера"""
        if self.timer_running and not self.is_game_over:
            self.seconds += 1
            minutes = self.seconds // 60
            seconds = self.seconds % 60
            self.timer_label.config(text=f"Время: {minutes:02d}:{seconds:02d}")
            self.window.after(1000, self.update_timer)
    
    def stop_timer(self):
        """Остановка таймера"""
        self.timer_running = False
    
    def right_click(self, event):
        """Обработка правого клика (установка/снятие флага)"""
        if self.is_game_over:
            return
        
        cur_btn = event.widget
        if cur_btn['state'] == 'normal' and not cur_btn.is_open:
            if not cur_btn.is_flagged and self.flags_placed < self.config.MINES:
                cur_btn['text'] = '🚩'
                cur_btn['state'] = 'disabled'
                cur_btn.is_flagged = True
                self.flags_placed += 1
            elif cur_btn.is_flagged:
                cur_btn['text'] = ''
                cur_btn['state'] = 'normal'
                cur_btn.is_flagged = False
                self.flags_placed -= 1
            
            self.mine_counter.config(text=f"Мины: {self.flags_placed}/{self.config.MINES}")
    
    def click(self, clicked_button):
        """Обработка левого клика"""
        if self.is_game_over or clicked_button.is_flagged:
            return
        
        if self.is_first_click:
            self.start_timer()
            self.insert_mines(clicked_button.number)
            self.count_mines_in_buttons()
            self.is_first_click = False
        
        if clicked_button.is_mine:
            self.game_over(clicked_button)
        else:
            self.reveal_cell(clicked_button)
            self.check_win()
    
    def reveal_cell(self, btn):
        """Открытие ячейки"""
        if btn.is_open or btn.is_flagged:
            return
        
        btn.is_open = True
        btn.config(state="disabled", relief=tk.SUNKEN)
        
        if btn.count_bomb > 0:
            color = self.config.COLORS.get(btn.count_bomb, "black")
            btn.config(text=btn.count_bomb, disabledforeground=color)
        else:
            # Открываем соседние пустые клетки
            self.reveal_empty_cells(btn)
    
    def reveal_empty_cells(self, btn):
        """Открытие соседних пустых клеток (BFS)"""
        queue = [btn]
        while queue:
            cur_btn = queue.pop()
            
            # Открываем все соседние клетки
            x, y = cur_btn.x, cur_btn.y
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    
                    neighbor = self.buttons[x + dx][y + dy]
                    if (not neighbor.is_open and not neighbor.is_flagged and 
                        1 <= neighbor.x <= self.config.ROW and 
                        1 <= neighbor.y <= self.config.COLUMNS and 
                        neighbor not in queue):
                        
                        neighbor.is_open = True
                        neighbor.config(state="disabled", relief=tk.SUNKEN)
                        
                        if neighbor.count_bomb > 0:
                            color = self.config.COLORS.get(neighbor.count_bomb, "black")
                            neighbor.config(text=neighbor.count_bomb, 
                                          disabledforeground=color)
                        else:
                            queue.append(neighbor)
    
    def game_over(self, clicked_button):
        """Обработка конца игры (проигрыш)"""
        self.is_game_over = True
        self.stop_timer()
        
        clicked_button.config(text="💥", background="red", 
                            disabledforeground="black")
        
        # Показываем все мины
        for i in range(1, self.config.ROW + 1):
            for j in range(1, self.config.COLUMNS + 1):
                btn = self.buttons[i][j]
                if btn.is_mine and not btn.is_flagged:
                    btn.config(text="💣", background="pink")
                elif not btn.is_mine and btn.is_flagged:
                    btn.config(text="❌", background="lightgray")
        
        showinfo('Конец игры', 'Вы наступили на мину! Игра окончена.')
    
    def check_win(self):
        """Проверка условий победы"""
        cells_to_open = self.config.ROW * self.config.COLUMNS - self.config.MINES
        opened_cells = 0
        
        for i in range(1, self.config.ROW + 1):
            for j in range(1, self.config.COLUMNS + 1):
                if self.buttons[i][j].is_open:
                    opened_cells += 1
        
        if opened_cells == cells_to_open:
            self.win_game()
    
    def win_game(self):
        """Обработка победы"""
        self.is_game_over = True
        self.stop_timer()
        
        # Показать все флаги на минах
        for i in range(1, self.config.ROW + 1):
            for j in range(1, self.config.COLUMNS + 1):
                btn = self.buttons[i][j]
                if btn.is_mine and not btn.is_flagged:
                    btn.config(text="🚩", background="lightgreen")
        
        showinfo('Победа!', 
                f'Вы выиграли!\nВремя: {self.seconds} сек.\nНажмите "Новая игра" чтобы сыграть еще раз.')
    
    def insert_mines(self, exclude_number):
        """Расстановка мин"""
        indexes = self.get_mines_places(exclude_number)
        for i in range(1, self.config.ROW + 1):
            for j in range(1, self.config.COLUMNS + 1):
                btn = self.buttons[i][j]
                if btn.number in indexes:
                    btn.is_mine = True
    
    def get_mines_places(self, exclude_number):
        """Генерация позиций мин"""
        indexes = list(range(1, self.config.COLUMNS * self.config.ROW + 1))
        indexes.remove(exclude_number)
        shuffle(indexes)
        return indexes[:self.config.MINES]
    
    def count_mines_in_buttons(self):
        """Подсчет мин вокруг каждой клетки"""
        for i in range(1, self.config.ROW + 1):
            for j in range(1, self.config.COLUMNS + 1):
                btn = self.buttons[i][j]
                count_bomb = 0
                if not btn.is_mine:
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            neighbor = self.buttons[i + dx][j + dy]
                            if neighbor.is_mine:
                                count_bomb += 1
                btn.count_bomb = count_bomb
    
    def open_settings(self):
        """Открытие окна настроек"""
        settings_win = tk.Toplevel(self.window)
        settings_win.title("Настройки игры")
        settings_win.geometry("300x200")
        settings_win.resizable(False, False)
        
        tk.Label(settings_win, text="Количество строк:").grid(row=0, column=0, 
                                                             padx=10, pady=10, sticky='w')
        row_entry = tk.Entry(settings_win)
        row_entry.insert(0, str(self.config.ROW))
        row_entry.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(settings_win, text="Количество колонок:").grid(row=1, column=0, 
                                                               padx=10, pady=10, sticky='w')
        col_entry = tk.Entry(settings_win)
        col_entry.insert(0, str(self.config.COLUMNS))
        col_entry.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(settings_win, text="Количество мин:").grid(row=2, column=0, 
                                                           padx=10, pady=10, sticky='w')
        mines_entry = tk.Entry(settings_win)
        mines_entry.insert(0, str(self.config.MINES))
        mines_entry.grid(row=2, column=1, padx=10, pady=10)
        
        def save_settings():
            try:
                rows = int(row_entry.get())
                cols = int(col_entry.get())
                mines = int(mines_entry.get())
                
                if rows < 5 or rows > 20:
                    showerror("Ошибка", "Количество строк должно быть от 5 до 20")
                    return
                if cols < 5 or cols > 30:
                    showerror("Ошибка", "Количество колонок должно быть от 5 до 30")
                    return
                if mines < 1 or mines >= rows * cols:
                    showerror("Ошибка", f"Количество мин должно быть от 1 до {rows*cols-1}")
                    return
                
                self.config.ROW = rows
                self.config.COLUMNS = cols
                self.config.MINES = mines
                self.config.save_to_file()
                
                settings_win.destroy()
                self.restart_game()
                
            except ValueError:
                showerror("Ошибка", "Пожалуйста, введите целые числа")
        
        save_btn = tk.Button(settings_win, text="Сохранить", 
                           command=save_settings, width=15)
        save_btn.grid(row=3, column=0, columnspan=2, pady=20)
    
    def show_rules(self):
        """Показать правила игры"""
        rules = """
        Правила игры "Сапер":
        
        1. Цель игры - открыть все клетки, не содержащие мин.
        2. Левый клик - открыть клетку.
        3. Правый клик - поставить/убрать флаг (🚩).
        4. Цифра в клетке показывает, сколько мин находится в соседних клетках.
        5. Если вы открываете клетку с миной - игра проиграна.
        6. Если пометить все мины флагами и открыть все безопасные клетки - вы победили!
        
        Удачи!
        """
        showinfo("Правила игры", rules)
    
    def show_about(self):
        """Показать информацию о программе"""
        about_text = """
        Сапер
        
        Версия 1.0
        Разработчик: Ваше Имя
        
        Классическая игра "Сапер" с графическим интерфейсом.
        Реализована на Python с использованием библиотеки tkinter.
        
        © 2024 Все права защищены.
        """
        showinfo("О программе", about_text)
    
    def restart_game(self):
        """Перезапуск игры"""
        self.is_game_over = False
        self.is_first_click = True
        self.flags_placed = 0
        self.seconds = 0
        self.stop_timer()
        
        self.create_buttons()
        self.timer_label.config(text="Время: 00:00")
        self.mine_counter.config(text=f"Мины: 0/{self.config.MINES}")
    
    def run(self):
        """Запуск игры"""
        self.window.mainloop()

if __name__ == "__main__":
    game = MineSweeper()
    game.run()
