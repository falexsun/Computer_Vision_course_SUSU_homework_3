import os
from pathlib import Path
from collections import Counter

# Путь к датасету
dataset_path = Path("ExDark-12")

# Классы из data.yaml
classes = [
    "Bicycle", "Boat", "Bottle", "Bus", "Cat", "Cup",
    "Motorbike", "People", "Table", "car", "chair", "dog"
]

# Подсчет объектов по классам
class_counts = Counter()

# Проходим по всем splits
for split in ['train', 'valid', 'test']:
    labels_dir = dataset_path / split / "labels"

    if not labels_dir.exists():
        print(f"Папка не найдена: {labels_dir}")
        continue

    print(f"\nАнализ {split}:")
    label_files = list(labels_dir.glob("*.txt"))
    print(f"  Найдено файлов аннотаций: {len(label_files)}")

    for label_file in label_files:
        with open(label_file, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 5:
                    class_id = int(parts[0])
                    if class_id < len(classes):
                        class_counts[class_id] += 1

# Вывод результатов
print("\n" + "="*70)
print("СТАТИСТИКА ПО КЛАССАМ")
print("="*70)

# Сортируем по популярности
sorted_classes = sorted(class_counts.items(), key=lambda x: x[1], reverse=True)

for class_id, count in sorted_classes:
    print(f"{classes[class_id]:15s}: {count:6d} объектов")

print("\n" + "="*70)
print("ТОП-5 САМЫХ ПОПУЛЯРНЫХ КЛАССОВ:")
print("="*70)

top5_ids = [cls_id for cls_id, _ in sorted_classes[:5]]
top5_names = [classes[cls_id] for cls_id in top5_ids]

for i, (cls_id, count) in enumerate(sorted_classes[:5], 1):
    print(f"{i}. {classes[cls_id]:15s}: {count:6d} объектов")

print("\nВыбранные классы:", ", ".join(top5_names))
print("ID классов:", top5_ids)
