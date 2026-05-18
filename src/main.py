import logging
import json
from pathlib import Path
from scanner import ArchivalDocumentScanner
from gemini_client import GeminiArchivalParser

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ArchivalPipelineApp:
    def __init__(self, target_language: str = "ru-old"):
        self.scanner = ArchivalDocumentScanner(target_language=target_language)
        self.parser = GeminiArchivalParser()
        self.consolidated_classifier = []

    def run_pipeline(self, folder_path: str):
        """Запуск сквозного конвейера обработки документов"""
        print("\n=== ЗАПУСК КОНВЕЙЕРА AI DOCUMENT INDEXER ===")
        
        # Шаг 1: Сканирование директории (Ишью #1)
        try:
            file_queue = self.scanner.scan_directory(folder_path)
        except Exception as e:
            logging.error(f"Критическая ошибка при сканировании: {e}")
            return

        if not file_queue:
            return

        total_files = len(file_queue)
        logging.info(f"Начало обработки ИИ. Всего файлов в очереди: {total_files}")

        # Шаг 2: Циклическая обработка файлов в Gemini API (Ишью #2)
        for index, file_meta in enumerate(file_queue, start=1):
            file_path = file_meta["file_path"]
            file_name = file_meta["file_name"]
            lang = file_meta["target_language"]

            # Эмуляция прогресс-бара и информирования (наша История №4)
            progress = (index / total_files) * 100
            print(f"\n[{progress:.1f}%] Обработка файла {index} из {total_files}: {file_name}")

            # Отправляем файл в ИИ-парсер
            extracted_records = self.parser.parse_document(file_path, target_language=lang)

            # Шаг 3: Агрегация данных в Единый источник истины (Модель данных)
            if extracted_records:
                for record in extracted_records:
                    # Добавляем запись в наш единый классификатор из 5 полей
                    self.consolidated_classifier.append({
                        "FIO": record.get("fio", ""),
                        "Rank_Position": record.get("rank_position", ""),
                        "Locality": record.get("locality", ""),
                        "Doc_Number": record.get("doc_number", ""),
                        "Doc_Date": record.get("doc_date", "")
                    })
            else:
                # Фиксация ошибок без падения конвейера (наша История №5)
                logging.warning(f"Файл {file_name} не вернул данных и был пропущен.")

        # Шаг 4: Вывод результатов
        print("\n=== ОБРАБОТКА ПОЛНОСТЬЮ ЗАВЕРШЕНА ===")
        print(f"Успешно сформирован единый классификатор. Всего записей: {len(self.consolidated_classifier)}")
        print(json.dumps(self.consolidated_classifier, ensure_ascii=False, indent=2))
        return self.consolidated_classifier

if __name__ == "__main__":
    # Запуск тестового прогона приложения
    app = ArchivalPipelineApp(target_language="ru-old")
    
    # В качестве теста сканируем корень нашего проекта
    app.run_pipeline("./")
