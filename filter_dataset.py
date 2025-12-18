import os
import shutil
from pathlib import Path
from tqdm import tqdm

# Исходный датасет
source_dataset = Path("ExDark-12")

# Целевая папка для фильтрованного датасета
target_dataset = Path("dataset")

# Исходные классы
all_classes = [
    "Bicycle", "Boat", "Bottle", "Bus", "Cat", "Cup",
    "Motorbike", "People", "Table", "car", "chair", "dog"
]

# Топ-5 классов (по результатам анализа)
# ID в исходном датасете: [7, 9, 10, 8, 2]
# Названия: People, car, chair, Table, Bottle
selected_class_ids = [7, 9, 10, 8, 2]  # People, car, chair, Table, Bottle
selected_class_names = [all_classes[i] for i in selected_class_ids]

# Создаем новый маппинг классов (0-4)
old_to_new_id = {old_id: new_id for new_id, old_id in enumerate(selected_class_ids)}

print("="*70)
print("ФИЛЬТРАЦИЯ ДАТАСЕТА")
print("="*70)
print(f"Исходный датасет: {source_dataset}")
print(f"Целевой датасет: {target_dataset}")
print(f"\nВыбранные классы:")
for new_id, old_id in enumerate(selected_class_ids):
    print(f"  {new_id}: {all_classes[old_id]} (старый ID: {old_id})")
print("="*70)

# Создаем структуру папок
for split in ['train', 'val', 'test']:
    (target_dataset / 'images' / split).mkdir(parents=True, exist_ok=True)
    (target_dataset / 'labels' / split).mkdir(parents=True, exist_ok=True)

# Маппинг splits (valid -> val)
split_mapping = {
    'train': 'train',
    'valid': 'val',
    'test': 'test'
}

# Статистика
stats = {
    'train': {'images': 0, 'objects': 0},
    'val': {'images': 0, 'objects': 0},
    'test': {'images': 0, 'objects': 0}
}

# Обработка каждого split
for source_split, target_split in split_mapping.items():
    print(f"\nОбработка {source_split} -> {target_split}...")

    source_images = source_dataset / source_split / "images"
    source_labels = source_dataset / source_split / "labels"

    target_images = target_dataset / 'images' / target_split
    target_labels = target_dataset / 'labels' / target_split

    if not source_images.exists():
        print(f"  ❌ Папка не найдена: {source_images}")
        continue

    # Получаем все изображения
    image_files = list(source_images.glob("*.jpg")) + list(source_images.glob("*.png"))

    print(f"  Найдено изображений: {len(image_files)}")

    # Обработка каждого изображения
    for img_file in tqdm(image_files, desc=f"  {target_split}"):
        label_file = source_labels / f"{img_file.stem}.txt"

        if not label_file.exists():
            continue

        # Читаем аннотации
        filtered_annotations = []

        with open(label_file, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 5:
                    old_class_id = int(parts[0])

                    # Проверяем входит ли класс в выбранные
                    if old_class_id in old_to_new_id:
                        # Переиндексируем класс
                        new_class_id = old_to_new_id[old_class_id]
                        new_line = f"{new_class_id} {' '.join(parts[1:])}\n"
                        filtered_annotations.append(new_line)

        # Если есть хотя бы одна аннотация из нужных классов
        if filtered_annotations:
            # Копируем изображение
            shutil.copy2(img_file, target_images / img_file.name)

            # Сохраняем отфильтрованные аннотации
            target_label_file = target_labels / f"{img_file.stem}.txt"
            with open(target_label_file, 'w') as f:
                f.writelines(filtered_annotations)

            stats[target_split]['images'] += 1
            stats[target_split]['objects'] += len(filtered_annotations)

# Создаем data.yaml
data_yaml_content = f"""path: {target_dataset.absolute()}
train: images/train
val: images/val
test: images/test

nc: 5
names: {selected_class_names}
"""

with open(target_dataset / 'data.yaml', 'w', encoding='utf-8') as f:
    f.write(data_yaml_content)

# Вывод статистики
print("\n" + "="*70)
print("РЕЗУЛЬТАТЫ ФИЛЬТРАЦИИ")
print("="*70)

for split in ['train', 'val', 'test']:
    print(f"\n{split.upper()}:")
    print(f"  Изображений: {stats[split]['images']}")
    print(f"  Объектов: {stats[split]['objects']}")

print("\n" + "="*70)
print("✅ Датасет отфильтрован и сохранен в папку 'dataset'")
print(f"✅ Файл data.yaml создан")
print("="*70)
