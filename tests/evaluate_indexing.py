import pandas as pd


def calculate_metrics(gt_path: str, pred_path: str) -> dict:
    """Вычисляет Precision и Recall для извлеченных ФИО и адресов."""
    # Загрузка эталона и предсказаний ИИ (формат CSV, UTF-8)
    gt_df = pd.read_csv(gt_path, encoding="utf-8")
    pred_df = pd.read_csv(pred_path, encoding="utf-8")

    # Переводим в множества кортежей для точного сопоставления
    # Предполагается структура колонок: ['fio', 'address']
    gt_entities = set(zip(gt_df["fio"].str.lower(), gt_df["address"].str.lower()))
    pred_entities = set(
        zip(pred_df["fio"].str.lower(), pred_df["address"].str.lower())
    )

    # Расчет пересечений
    true_positives = len(gt_entities.intersection(pred_entities))

    # Метрики NLP
    recall = true_positives / len(gt_entities) if gt_entities else 0
    precision = true_positives / len(pred_entities) if pred_entities else 0

    return {
        "Recall": recall,
        "Precision": precision,
        "Passed": recall >= 0.95 and precision >= 0.95,
    }


# Пример вызова для CI/CD pipeline
if __name__ == "__main__":
    metrics = calculate_metrics("tests/ground_truth.csv", "output/predictions.csv")
    print(f"Результаты валидации ИИ: {metrics}")
    assert metrics["Passed"], "Критерии приемки качества ИИ не выполнены!"
