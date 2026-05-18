import os
import logging
from pathlib import Path
from typing import List, Dict, Set

# 1. Настройка логирования ошибок (согласно ТЗ)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ArchivalDocumentScanner:
    def __init__(self, target_language: str = "ru-old"):
        self.target_language = target_language
        # Настройка форматов по умолчанию (.jpg, .jpeg) + возможность расширения
        self.allowed_extensions: Set[str] = {".jpg", ".jpeg"}
        self.load_security_keys()

    def load_security_keys(self):
        """Безопасная загрузка ключей согласно docs/security-policy.md"""
        # В реальном приложении здесь будет подгрузка из библиотеки python-dotenv
        gemini_key = os.getenv("GEMINI_API_KEY", "")
        if not gemini_key:
            logging.warning("API-ключ GEMINI_API_KEY не найден в переменных окружения или .env файле.")
        else:
            logging.info("API-ключ Gemini успешно обнаружен в безопасном контуре.")

    def add_allowed_extensions(self, extensions: List[str]):
        """Техническая возможность расширить список форматов (.png, .tiff) через настройки"""
        for ext in extensions:
            cleaned_ext = ext.lower() if ext.startswith(".") else f".{ext.lower()}"
            self.allowed_extensions.add(cleaned_ext)
        logging.info(f"Список разрешенных форматов обновлен: {self.allowed_extensions}")

    def scan_directory(self, folder_path_str: str) -> List[Dict[str, str]]:
        """Рекурсивное сканирование папки и сбор метаданных"""
        folder_path = Path(folder_path_str)
        
        # Обработка ошибок: Неверный путь / Папка не существует
        if not folder_path.exists() or not folder_path.is_dir():
            raise FileNotFoundError(f"Указанный путь не существует или не является папкой: {folder_path_str}")

        metadata_queue: List[Dict[str, str]] = []

        # Рекурсивный обход всех вложенных подкаталогов
        for file in folder_path.rglob("*"):
            try:
                # Фильтрация форматов (проверка расширения независимо от регистра)
                if file.is_file() and file.suffix.lower() in self.allowed_extensions:
                    
                    # Сбор метаданных согласно docs/data-model.md
                    file_metadata = {
                        "file_path": str(file.resolve()),       # Полный путь к файлу на диске
                        "file_name": file.name,                 # Имя файла с расширением
                        "target_language": self.target_language # Языковой профиль
                    }
                    metadata_queue.append(file_metadata)
                    
            except Exception as e:
                # Обработка ошибок: Поврежденный файл / Ошибка доступа. Конвейер не прерывается
                logging.error(f"Ошибка при обработке файла {file}: {e}. Файл пропущен.")
                continue

        # Обработка ошибок: Пустая папка
        if not metadata_queue:
            print("\n⚠️ Предупреждение: В указанной директории не обнаружено архивных документов.")
            return []

        logging.info(f"Сканирование успешно завершено. Найдено файлов для обработки ИИ: {len(metadata_queue)}")
        return metadata_queue


# --- ДЕМОНСТРАЦИЯ РАБОТЫ СКРИПТА ---
if __name__ == "__main__":
    print("--- Тестирование локального бэкенд-сканера ---")
    
    # Создаем экземпляр сканера
    scanner = ArchivalDocumentScanner(target_language="ru-old")
    
    # Демонстрация расширения настроек форматов (например, добавим .tiff)
    scanner.add_allowed_extensions([".tiff", "png"])
    
    # ТЕСТ 1: Эмуляция ввода пути пользователем (укажите вашу тестовую папку для проверки)
    test_folder = "./" # Текущая папка проекта
    
    try:
        results = scanner.scan_directory(test_folder)
        if results:
            print(f"\nПример первого объекта в очереди ИИ:\n{results[0]}")
    except Exception as error:
        print(f"Конвейер остановлен из-за критической ошибки: {error}")
