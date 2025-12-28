#!/usr/bin/env python3
"""
Точка входа для игры Сапер
"""

import sys
import os

def setup_paths():
    """Настройка путей для импорта"""
    # Получаем абсолютный путь к директории проекта
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Добавляем src в PYTHONPATH
    src_path = os.path.join(project_root, 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    # Создаем папку data если её нет
    data_path = os.path.join(project_root, 'data')
    if not os.path.exists(data_path):
        os.makedirs(data_path, exist_ok=True)
        
        # Создаем дефолтные настройки если файла нет
        default_settings = {
            "rows": 7,
            "columns": 10,
            "mines": 10,
            "version": "1.0.0",
            "last_updated": "2024-01-01"
        }
        
        import json
        settings_file = os.path.join(data_path, 'settings.json')
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(default_settings, f, indent=4, ensure_ascii=False)

def main():
    """Основная функция запуска игры"""
    print("=" * 40)
    print("       ЗАПУСК ИГРЫ 'САПЕР'")
    print("=" * 40)
    
    try:
        setup_paths()
        
        from game import MineSweeper
        
        game = MineSweeper()
        game.run()
        
    except ImportError as e:
        print(f"Ошибка импорта: {e}")
        print("Проверьте структуру проекта:")
        print("- Папка 'src' должна содержать game.py")
        print("- Папка 'data' должна существовать")
        
    except Exception as e:
        print(f"Ошибка при запуске игры: {e}")
        
    finally:
        input("\nНажмите Enter для выхода...")
        sys.exit(1 if 'Exception' in locals() else 0)

if __name__ == "__main__":
    main()
