import os
import json
import logging
import time
from pathlib import Path
from typing import List, Dict, Any

# Импортируем официальный клиент Google GenAI
# (Для работы требуется установка: pip install google-genai)
try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GeminiArchivalParser:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.client = None
        self.system_instruction = self._load_system_prompt()
        self._init_client()

    def _load_system_prompt(self) -> str:
        """Автоматическая загрузка инструкций из docs/system-prompt.md"""
        # Ищем файл промпта относительно корня проекта
        prompt_path = Path(__file__).parent.parent / "docs" / "system-prompt.md"
        if prompt_path.exists():
            with open(prompt_path, "r", encoding="utf-8") as f:
                content = f.read()
                # Извлекаем чистый текст промпта из блока кода
                if "```text" in content:
                    return content.split("```text")[1].split("```")[0].strip()
                return content
        
        # Резервный вариант, если файл не найден
        return "Ты старший архивист. Извлеки FIO, rank_position, locality, doc_number, doc_date в формате JSON."

    def _init_client(self):
        """Безопасная инициализация согласно docs/security-policy.md"""
        if not self.api_key:
            logging.error("Критическая ошибка: GEMINI_API_KEY не найден в .env.")
            return
        
        if genai is None:
            logging.warning("Библиотека google-genai не установлена. Работа в эмуляционном режиме.")
            return

        # Инициализируем официальный клиент Google
        self.client = genai.Client(api_key=self.api_key)
        logging.info("Клиент Gemini API успешно инициализирован.")

    def parse_document(self, file_path_str: str, target_language: str = "ru-old") -> List[Dict[str, Any]]:
        """Отправка скана в Gemini API и извлечение 5 полей данных с поддержкой Retry"""
        file_path = Path(file_path_str)
        
        if not file_path.exists():
            logging.error(f"Файл не найден: {file_path_str}")
            return []

        # Настройка модели: Flash идеален по скорости и стоимости для OCR задач
        model_name = "gemini-1.5-flash"
        
        # Реализация Edge Case: 3 попытки подключения при сбоях сети (Retry)
        for attempt in range(1, 4):
            try:
                if not self.client:
                    # Если клиент не инициализирован, эмулируем успешный ответ для тестов
                    return self._get_mock_response(file_path.name, target_language)

                # Загружаем графический файл в поток байт
                with open(file_path, "rb") as img_file:
                    image_bytes = img_file.read()

                image_part = types.Part.from_bytes(
                    data=image_bytes,
                    mime_type="image/jpeg" if file_path.suffix.lower() in [".jpg", ".jpeg"] else "image/png"
                )

                # Формируем конфигурацию запроса со строгим требованием JSON
                config = types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    temperature=0.1,  # Низкая температура для максимальной точности OCR
                    response_mime_type="application/json" # Требуем строго JSON на выходе
                )

                prompt = f"Проанализируй этот архивный документ. Языковой профиль: {target_language}."
                
                # Запрос к ИИ (передаем текст промпта и саму картинку)
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=[prompt, image_part],
                    config=config
                )

                # Реализация Edge Case: Валидация JSON-ответа от ИИ
                raw_text = response.text.strip()
                parsed_json = json.loads(raw_text)
                
                logging.info(f"Файл {file_path.name} успешно обработан ИИ.")
                return parsed_json if isinstance(parsed_json, list) else [parsed_json]

            except json.JSONDecodeError:
                logging.error(f"Ошибка: ИИ вернул некорректный формат JSON для файла {file_path.name}. Файл пропущен.")
                return []
            except Exception as e:
                logging.warning(f"Попытка {attempt} не удалась из-за ошибки сети/API: {e}")
                if attempt < 3:
                    time.sleep(2 ** attempt) # Экспоненциальная задержка перед повтором
                else:
                    logging.error(f"Не удалось обработать файл {file_path.name} после 3 попыток.")
                    return []
        return []

    def _get_mock_response(self, filename: str, lang: str) -> List[Dict[str, Any]]:
        """Эмуляция ответа ИИ для локального тестирования без ключа API"""
        return [{
            "fio": "Иванов Петр Сергеевич",
            "rank_position": "Старший унтер-офицер",
            "locality": "с. Петровское",
            "doc_number": "№ 5",
            "doc_date": "10.05.1915" if lang == "ru-old" else "10.05.1985"
        }]

# Демонстрация работы модуля
if __name__ == "__main__":
    print("--- Тестирование ИИ-клиента Gemini ---")
    parser = GeminiArchivalParser()
    # Эмулируем обработку тестового скана
    mock_results = parser.parse_document("test_scan.jpg", target_language="ru-old")
    print(f"Результат парсинга:\n{json.dumps(mock_results, ensure_ascii=False, indent=2)}")
