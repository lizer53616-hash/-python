#!/usr/bin/env python3
"""
Точка входа для игры Сапер
"""

import sys
import os

# Добавляем src в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from game import MineSweeper

def main():
    """Основная функция запуска игры"""
    print("Запуск игры Сапер...")
    print("=" * 40)
    
    try:
        game = MineSweeper()
        game.run()
    except Exception as e:
        print(f"Ошибка при запуске игры: {e}")
        input("Нажмите Enter для выхода...")
        sys.exit(1)

if __name__ == "__main__":
    main()
