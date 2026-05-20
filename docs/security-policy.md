# Политика безопасности и ограничение ответственности (Security Policy & Disclaimer)

Данный документ определяет границы ответственности разработчиков системы `AI Document Indexer` в отношении обработки, хранения и передачи данных, а также устанавливает требования безопасности для разработчиков и пользователей.

---
 
## ⚖️ Ограничение ответственности (Disclaimer)

1. **Легитимность источников данных:** Система не осуществляет сбор, поиск или предоставление архивных документов. Пользователь несет полную ответственность за легальность и надлежащее происхождение загружаемых в систему документов.

2. **Отсутствие встроенной защиты ПДн:** В системе не предусмотрены встроенные механизмы маскирования, депермонализации или анонимизации персональных данных. Система передает исходные данные (текст и графику) во внешние API без предварительной санитизации.

3. **Ответственность за комплаенс:** Вся ответственность за соблюдение законодательства о персональных данных (GDPR, CCPA, российского ФЗ-152 и т.д.) лежит исключительно на пользователе и организации, использующей систему.

4. **Риск передачи данных третьим лицам:** При использовании Google Gemini API пользователь согласен с передачей своих данных серверам Google LLC. Разработчики системы не несут ответственность за безопасность этих данных за пределами приложения.

---

## 🔒 Технические особенности обработки данных

Для понимания рисков безопасности пользователю необходимо учитывать архитектуру сквозного процесса:

* **Передача данных во внешние контуры:** Конвейер обработки включает в себя передачу текстового и графического контента на серверы Google для обработки моделью Gemini. Эти данные находятся вне контроля разработчиков.

* **Хранение данных в памяти:** Во время обработки данные хранятся в памяти приложения. При критических ошибках или сбое системы часть данных может остаться в swap-памяти или кэше ОС.

* **Рекомендация для пользователей:** Настоятельно **не рекомендуется** загружать в систему документы, содержащие:
  - Номера паспортов, социальных страховых номеров
  - Банковские реквизиты или платежную информацию
  - Медицинские или биометрические данные
  - Конфиденциальную служебную информацию

---

## 🔑 Безопасность API-ключей и учетных данных (API Key Management)

Поскольку конвейер обработки данных использует внешние модели ИИ через API-интерфейсы, разработчики и пользователи должны следовать строгим правилам управления секретами.

### Основные правила:

1. **Запрет на жесткое кодирование (Hardcoding):** Категорически запрещено записывать API-ключи, токены доступа или пароли непосредственно в исходный код, конфигурационные файлы или комментарии. Нарушение этого правила приводит к компрометации учетных данных в системе версионирования.

2. **Использование переменных окружения:** Все конфиденциальные данные (API-ключи, токены, пароли) должны считываться приложением из переменных окружения, которые устанавливаются на уровне ОС или через файл `.env` (только в локальной разработке).

3. **Защита репозитория (.gitignore):** Локальный файл `.env`, содержащий реальные ключи доступа, должен быть в обязательном порядке добавлен в `.gitignore`. Вместо него в репозитории должен находиться файл `.env.example` с фиктивными значениями для иллюстрации структуры.

### Содержимое .gitignore (для секретов):

```gitignore
# Environment variables with real credentials
.env
.env.local
.env.*.local

# IDE and OS specific
.vscode/
.idea/
*.swp
*.swo
__pycache__/
*.pyc

# Temporary files
temp/
tmp/
*.tmp

# Logs with sensitive info
logs/
*.log
```

### Пример структуры .env файла:

```bash
# Создайте файл .env в корне проекта и заполните реальными значениями:
GEMINI_API_KEY=AIzaSy_YOUR_ACTUAL_KEY_HERE_1234567890abcdefghij
APP_ENV=development
LOG_LEVEL=INFO
SESSION_SECRET_KEY=your_random_32_character_secret_key_here_abcd1234
```

---

## 💾 Безопасная загрузка API-ключей (Secure Key Loading)

### Вариант 1: Использование python-dotenv (рекомендуется)

```python
# src/config.py
from pathlib import Path
from dotenv import load_dotenv
import os
import sys

# Загружаем переменные окружения из .env файла
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

def get_gemini_api_key() -> str:
    """
    Безопасно загружает API-ключ Gemini из переменной окружения.
    
    Raises:
        EnvironmentError: Если ключ не найден или пуст
    """
    api_key = os.getenv('GEMINI_API_KEY', '').strip()
    
    if not api_key or api_key.startswith('PLACEHOLDER'):
        raise EnvironmentError(
            "ОШИБКА: Переменная окружения GEMINI_API_KEY не установлена или содержит значение PLACEHOLDER.\n"
            "Решение:\n"
            "1. Скопируйте .env.example в .env\n"
            "2. Откройте .env в текстовом редакторе\n"
            "3. Замените PLACEHOLDER на реальный API-ключ Gemini\n"
            "4. Сохраните файл (НЕ коммитьте .env в git!)"
        )
    
    return api_key

def get_config() -> dict:
    """Возвращает полную конфигурацию приложения из переменных окружения"""
    try:
        config = {
            'gemini_api_key': get_gemini_api_key(),
            'app_env': os.getenv('APP_ENV', 'development'),
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            'max_file_size_mb': int(os.getenv('MAX_FILE_SIZE_MB', '100')),
            'session_secret': os.getenv('SESSION_SECRET_KEY', 'dev-secret-key'),
            'default_language': os.getenv('DEFAULT_DOCUMENT_LANGUAGE', 'ru-modern'),
        }
        return config
    except (ValueError, TypeError) as e:
        raise ValueError(f"Ошибка при парсинге конфигурации: {e}")

# Пример использования:
# from src.config import get_gemini_api_key
# 
# try:
#     key = get_gemini_api_key()
#     print("API-ключ успешно загружен")
# except EnvironmentError as e:
#     print(f"Ошибка конфигурации: {e}")
#     sys.exit(1)
```

### Вариант 2: Без внешних зависимостей (встроенный pathlib и os)

```python
# src/config_simple.py
import os
from pathlib import Path

class ConfigError(Exception):
    """Исключение для ошибок конфигурации"""
    pass

class SecureConfig:
    """Безопасный загрузчик конфигурации из переменных окружения"""
    
    @staticmethod
    def load_env_file(env_path: str = '.env') -> None:
        """Загружает переменные из .env файла в os.environ"""
        env_file = Path(env_path)
        
        if not env_file.exists():
            raise FileNotFoundError(
                f"Файл .env не найден по пути: {env_file.resolve()}\n"
                "Решение: Скопируйте .env.example в .env и заполните реальными значениями"
            )
        
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Пропускаем пустые строки и комментарии
                    if not line or line.startswith('#'):
                        continue
                    
                    # Парсим переменную (KEY=VALUE)
                    if '=' not in line:
                        print(f"⚠️  Строка {line_num} в .env: игнорируется (неверный формат)")
                        continue
                    
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')  # Удаляем кавычки
                    
                    # Устанавливаем переменную окружения
                    os.environ[key] = value
        
        except IOError as e:
            raise ConfigError(f"Ошибка при чтении .env файла: {e}")
    
    @staticmethod
    def get_gemini_api_key() -> str:
        """Безопасно получает API-ключ Gemini"""
        api_key = os.environ.get('GEMINI_API_KEY', '').strip()
        
        if not api_key:
            raise ConfigError(
                "❌ GEMINI_API_KEY не найден в переменных окружения.\n"
                "Решение:\n"
                "  1. cp .env.example .env\n"
                "  2. Отредактируйте .env и замените PLACEHOLDER на реальный ключ\n"
                "  3. Убедитесь, что .env добавлен в .gitignore"
            )
        
        if api_key.startswith('PLACEHOLDER'):
            raise ConfigError(
                "❌ GEMINI_API_KEY содержит значение PLACEHOLDER.\n"
                "Это означает, что вы забыли заменить фиктивное значение на реальный ключ.\n"
                "Решение: Отредактируйте .env и вставьте реальный API-ключ."
            )
        
        return api_key

# Пример использования:
# if __name__ == '__main__':
#     try:
#         SecureConfig.load_env_file('.env')
#         key = SecureConfig.get_gemini_api_key()
#         print("✅ Конфигурация успешно загружена")
#     except (FileNotFoundError, ConfigError) as e:
#         print(f"❌ Ошибка: {e}")
#         exit(1)
```

---

## 🚨 Политика реагирования на найденные уязвимости (Vulnerability Response Policy)

Если вы обнаружили критическую уязвимость в коде или конфигурации, немедленно следуйте этому алгоритму:

### Шаг 1: Сообщение об уязвимости

1. **НЕ создавайте публичный issue** с описанием критической уязвимости!
2. **Свяжитесь с мейнтейнером напрямую** через email или приватное сообщение на GitHub
3. **Предоставьте подробное описание:**
   - Как воспроизвести уязвимость (CVSS score, если применимо)
   - Доказательство концепции (PoC), если возможно
   - Ваш контакт для уточнений

### Шаг 2: Приоритизация и оценка

| Уровень | Описание | Время на исправление |
|---------|---------|---------------------|
| **CRITICAL** | Полная компрометация системы, утечка всех API-ключей, удаление данных | ≤ 24 часа |
| **HIGH** | Несанкционированный доступ, утечка части данных, отказ в обслуживании | ≤ 72 часа |
| **MEDIUM** | Локальное получение привилегий, информационное раскрытие | ≤ 2 недели |
| **LOW** | Незначительные проблемы, эстетические ошибки, улучшения | Следующий релиз |

### Шаг 3: Исправление и тестирование

1. Разработчик создает **приватную ветку** (не в main репозитории)
2. Пишет **unit-тесты**, которые выявляют уязвимость
3. Реализует исправление
4. Проверяет, что все тесты проходят
5. Выполняет **code review** перед мержем в main

### Шаг 4: Выпуск патча

1. Создается **новая версия** с инкрементом patch-версии (например, 1.0.1 → 1.0.2)
2. В **CHANGELOG** добавляется строка о безопасности: `Security: Fixed critical vulnerability in API key handling`
3. Выпускается **GitHub Release** с описанием проблемы и решения
4. **Пользователи уведомляются** (если есть список активных инсталляций)

### Шаг 5: Постмортем и документирование

1. Документируется, как была обнаружена уязвимость
2. Добавляются тесты, чтобы эта уязвимость не повторилась
3. Проводится review процесса разработки, чтобы предотвратить подобное в будущем

### Файл SECURITY.md (для контакта)

Добавьте в корень репозитория файл `SECURITY.md`:

```markdown
# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability, please email security@example.com 
instead of using the issue tracker.

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact

We will acknowledge your report within 24 hours and provide updates.
```

---

## 🛡️ Разграничение доступа и логирование (Access Control & Logging)

### 1. Разграничение доступа на уровне ОС

```bash
# Установить правильные права доступа на файлы
# Только владелец может читать .env файл
chmod 600 .env
chmod 644 .env.example

# Логи могут быть читаны владельцем и администратором
chmod 640 logs/*.log
chown $(whoami):adm logs/

# Директория с данными - только владелец
chmod 700 ./data
```

### 2. Обязательное логирование

**ВСЕГДА логируйте:**
- Попытки загрузки конфигурации (успех/неудача)
- Запросы к Gemini API (с маскировкой API-ключа)
- Ошибки и исключения с полным stack trace
- Запуск и завершение обработки файлов
- Логирование доступа к сессиям (session_id, timestamp)

```python
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def mask_api_key(key: str, visible_chars: int = 8) -> str:
    """Маскирует API-ключ для логирования"""
    if len(key) > visible_chars:
        return key[:visible_chars] + '*' * (len(key) - visible_chars)
    return '*' * len(key)

# Примеры логирования
logger.info(f"Gemini API key loaded: {mask_api_key(api_key)}")
logger.error(f"Failed to process file: {file_path}, Error: {str(e)}")
logger.warning(f"Session {session_id} expired after 24 hours")
```

**НИКОГДА не логируйте:**
- Полные API-ключи или токены
- Полные содержимое файлов с ПДн
- Пароли или учетные данные
- Приватные ключи или сертификаты

### 3. Анализ логов на аномалии

Регулярно проверяйте логи на:
- Повторяющиеся ошибки валидации (может указывать на атаку)
- Необычное количество запросов в короткий промежуток времени
- Ошибки при чтении .env (может указывать на попытку инъекции)
- Критические исключения

```bash
# Пример: поиск ошибок в логах
grep "ERROR\|CRITICAL" logs/app.log | tail -20

# Пример: анализ частоты ошибок
grep "Failed to process" logs/app.log | wc -l
```

---

## 🔐 Защита от Brute Force атак и Rate Limiting

### Валидация входных данных

```python
import re
from pathlib import Path

class InputValidator:
    """Валидатор для защиты от инъекций и эксплойтов"""
    
    MAX_PATH_LENGTH = 4096
    MAX_FILENAME_LENGTH = 255
    
    @staticmethod
    def validate_file_path(file_path: str) -> bool:
        """
        Проверяет корректность пути к файлу.
        Защита от path traversal (../, ..\) и других инъекций.
        """
        # Проверка длины
        if len(file_path) > InputValidator.MAX_PATH_LENGTH:
            return False
        
        # Проверка на path traversal
        if '..' in file_path:
            return False
        
        # Проверка, что файл существует и имеет правильное расширение
        try:
            path = Path(file_path).resolve()
            allowed_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.pdf'}
            if path.suffix.lower() not in allowed_extensions:
                return False
            if not path.exists():
                return False
            return True
        except (ValueError, OSError):
            return False
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """Базовая проверка формата API-ключа Gemini"""
        # Gemini ключи обычно начинаются с AIzaSy и содержат буквы, цифры, дефис
        pattern = r'^AIzaSy[A-Za-z0-9_-]{32,}$'
        return bool(re.match(pattern, api_key))
```

### Rate Limiting

```python
import time
from collections import defaultdict
from threading import Lock

class RateLimiter:
    """
    Простой rate limiter для защиты от DDoS-подобных атак.
    Ограничивает количество запросов с одного источника за определенный период.
    """
    
    def __init__(self, max_requests: int = 100, time_window_seconds: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window_seconds
        self.requests = defaultdict(list)
        self.lock = Lock()
    
    def is_allowed(self, identifier: str) -> bool:
        """
        Проверяет, разрешен ли запрос для данного идентификатора (IP, user_id и т.д.)
        
        Args:
            identifier: IP адрес, user_id или другой уникальный идентификатор
        
        Returns:
            True если запрос разрешен, False если превышен лимит
        """
        with self.lock:
            now = time.time()
            
            # Удаляем старые запросы за пределами окна времени
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if now - req_time < self.time_window
            ]
            
            # Проверяем, не превышен ли лимит
            if len(self.requests[identifier]) < self.max_requests:
                self.requests[identifier].append(now)
                return True
            
            return False

# Пример использования:
# rate_limiter = RateLimiter(max_requests=10, time_window_seconds=60)
# 
# if rate_limiter.is_allowed(user_ip):
#     process_request()
# else:
#     return HttpError(429, "Too Many Requests")
```

---

## 📖 Инструкция для пользователя: Как получить API-ключ Gemini

Для работы программы вам понадобится личный бесплатный ключ доступа к искусственному интеллекту Google Gemini. Следуйте этим шагам:

1. **Перейдите на сайт разработчиков:** Откройте в браузере страницу **[Google AI Studio](https://aistudio.google.com)** и войдите под своей учетной записью Google (создайте, если не имеете).

2. **Создайте ключ:** В левом меню нажмите на кнопку **"Get API key"** или **"API keys"**.

3. **Сгенерируйте токен:** Нажмите кнопку **"Create API key"**, выберите в списке проект по умолчанию и подтвердите создание.

4. **Скопируйте ключ:** Перед вами появится длинная строка из букв и цифр (например, `AIzaSy...`). Нажмите кнопку **"Copy"** для копирования в буфер обмена.

5. **Активация в программе:** 
   - Скопируйте файл `.env.example` в `.env`:
     ```bash
     cp .env.example .env
     ```
   - Откройте файл `.env` в текстов��м редакторе
   - Найдите строку: `GEMINI_API_KEY=PLACEHOLDER_AIzaSy_YOUR_ACTUAL_API_KEY_HERE_1234567890`
   - Замените `PLACEHOLDER_AIzaSy_YOUR_ACTUAL_API_KEY_HERE_1234567890` на скопированный ключ
   - Сохраните файл

6. **Убедитесь в безопасности:**
   - Проверьте, что `.env` добавлен в `.gitignore` (файл не должен попадать в git)
   - Никогда не делитесь содержимым `.env` файла с кем-либо
   - Если ключ был случайно опубликован, немедленно удалите его на сайте AI Studio и создайте новый

---

## ✅ Чеклист для разработчиков (Developer Security Checklist)

Перед каждым коммитом убедитесь, что вы выполнили все пункты:

- [ ] API-ключи и токены не жестко закодированы в исходном коде
- [ ] Файл `.env` добавлен в `.gitignore`
- [ ] Файл `.env.example` содержит только фиктивные значения (PLACEHOLDER)
- [ ] Все обращения к переменным окружения обернуты в try/except с инф��рмативными сообщениями об ошибках
- [ ] Логирование не содержит полные API-ключи (используйте mask_api_key())
- [ ] Пути к файлам проверяются на path traversal атаки
- [ ] Входные данные валидируются перед использованием
- [ ] Rate limiting применяется к критическим операциям
- [ ] Обработка исключений включена для всех I/O операций
- [ ] Код протестирован на dev-окружении перед пушем в main
- [ ] Нет случайно включенных отладочных данных (print(), pdb)
- [ ] Все новые секреты документированы в `.env.example`

---

## 📚 Ссылки на другие документы

👉 **[Пользовательские истории (User Stories)](user-stories.md)** — функциональные требования к системе  
👉 **[Архитектура системы (System Architecture)](architecture.md)** — детали реализации и взаимодействия компонентов  
👉 **[Модель данных (Data Model)](data-model.md)** — структуры входных и выходных данных  

---

**Версия документа:** 2.0  
**Дата обновления:** 2026-05-20  
**Статус:** Актуальна
