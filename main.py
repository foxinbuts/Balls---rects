import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
from PIL import Image
from scipy.ndimage import label
from skimage.measure import regionprops
import math

def analyze_shapes_advanced(image_path):
    img = Image.open(image_path).convert("RGB")
    pixels = np.array(img)
    gray = np.mean(pixels, axis=2)
    binary = gray > 0  # Считаем все цветные пиксели передним планом

    labeled_array, num_labels = label(binary)
    regions = regionprops(labeled_array, intensity_image=pixels)

    circles_by_color = Counter()
    rectangles_by_color = Counter()

    for region in regions:
        if region.area >= 20:  # Увеличил порог для фильтрации шума
            color = tuple(int(c) for c in region.mean_intensity)
            bbox_width = region.bbox[3] - region.bbox[1]
            bbox_height = region.bbox[2] - region.bbox[0]
            aspect_ratio = bbox_width / bbox_height if bbox_height > 0 else 1
            solidity = region.solidity
            eccentricity = region.eccentricity
            extent = region.extent # Добавлено свойство extent

            # Более строгая классификация на основе характеристик формы
            if eccentricity < 0.4 and solidity > 0.85 and 0.8 <= aspect_ratio <= 1.2:
                circles_by_color[color] += 1
            elif extent > 0.5 and 0.3 <= aspect_ratio <= 3 and solidity > 0.5 and eccentricity > 0.5:
                rectangles_by_color[color] += 1

    total_circles = sum(circles_by_color.values())
    total_rectangles = sum(rectangles_by_color.values())
    total_shapes = num_labels

    return {
        "total_shapes": total_shapes,
        "total_circles": total_circles,
        "total_rectangles": total_rectangles,
        "circles_by_color": dict(circles_by_color),
        "rectangles_by_color": dict(rectangles_by_color),
    }

image_file = "balls_and_rects.png"
analysis_result = analyze_shapes_advanced(image_file)

print(f"Общее количество фигур на изображении: {analysis_result['total_shapes']}")
print(f"Общее количество кругов: {analysis_result['total_circles']}")
print(f"Общее количество прямоугольников: {analysis_result['total_rectangles']}")
print("Количество кругов по оттенкам:", analysis_result['circles_by_color'])
print("Количество прямоугольников по оттенкам:", analysis_result['rectangles_by_color'])

# Визуализация (не обязательна для анализа)
try:
    img = plt.imread(image_file)
    plt.imshow(img)
    labeled_img, num_labels_vis = label(np.mean(np.array(Image.open(image_file).convert("RGB")), axis=2) > 0)
    regions_vis = regionprops(labeled_img)

    for region in regions_vis:
        minr, minc, maxr, maxc = region.bbox
        rect = plt.Rectangle((minc, minr), maxc - minc, maxr - minr,
                             fill=False, edgecolor='red', linewidth=1)
        plt.gca().add_patch(rect)

        if region.eccentricity < 0.4 and region.solidity > 0.85 and 0.8 <= (maxc - minc) / (maxr - minr + 1e-6) <= 1.2:
            cy, cx = region.centroid
            circle = plt.Circle((cx, cy), radius=math.sqrt(region.area / math.pi),
                                 fill=False, edgecolor='blue', linewidth=1)
            plt.gca().add_patch(circle)

    plt.title("Обнаруженные фигуры (красные - прямоугольники, синие - круги)")
    plt.axis('off')
    plt.show()

except FileNotFoundError:
    print(f"Файл не найден: {image_file}")
except Exception as e:
    print(f"Ошибка при отображении изображения: {e}")