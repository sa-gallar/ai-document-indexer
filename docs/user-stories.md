## 🗺️ Карта вариантов использования (Use Case Diagram)

Ниже представлена диаграмма, визуализирующая границы системы и основные сценарии взаимодействия конечных пользователей с приложением `AI Document Indexer`:

```mermaid
graph LR
    %% Акторы
    A1[Архивист / Сотрудник архива]
    A2[Исследователь родословной]

    %% Варианты использования (Функции системы)
    UC1(Выбрать папку с архивными файлами)
    UC2(Указать языковой профиль документа)
    UC3(Запустить конвейер ИИ-обработки)
    UC4(Контролировать прогресс обработки)
    UC5(Просмотреть сформированный классификатор)

    %% Связи для Первого Актора
    A1 --> UC1
    A1 --> UC2
    A1 --> UC3
    A1 --> UC4
    A1 --> UC5

    %% Связи для Второго Актора
    A2 --> UC1
    A2 --> UC2
    A2 --> UC3
    A2 --> UC4
    A2 --> UC5

    %% Стилизация элементов
    style A1 fill:#e1f5fe,stroke:#0288d1,stroke-width:1px
    style A2 fill:#e1f5fe,stroke:#0288d1,stroke-width:1px
    style UC1 fill:#fafafa,stroke:#333,stroke-width:1px
    style UC2 fill:#fafafa,stroke:#333,stroke-width:1px
    style UC3 fill:#fafafa,stroke:#333,stroke-width:1px
    style UC4 fill:#fafafa,stroke:#333,stroke-width:1px
    style UC5 fill:#fafafa,stroke:#333,stroke-width:1px
```
