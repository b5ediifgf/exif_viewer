import os
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import folium

def get_exif_data(image_path):
    try:
        img = Image.open(image_path)
        exif_data = img._getexif()
        if not exif_data:
            print("[-] В этом файле нет метаданных EXIF.")
            return None
        readable_exif = {}
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)
            readable_exif[tag_name] = value
        return readable_exif
    except Exception as e:
        print(f"[-] Ошибка при чтении файла: {e}")
        return None

def convert_to_degrees(value):
    d = float(value[0])
    m = float(value[1])
    s = float(value[2])
    return d + (m / 60.0) + (s / 3600.0)

def get_gps_coordinates(exif_data):
    if "GPSInfo" not in exif_data:
        print("[-] В метаданных фото отсутствуют GPS координаты.")
        return None
    gps_info = {}
    for tag, value in exif_data["GPSInfo"].items():
        tag_name = GPSTAGS.get(tag, tag)
        gps_info[tag_name] = value
    required_tags = ["GPSLatitude", "GPSLatitudeRef", "GPSLongitude", "GPSLongitudeRef"]
    if not all(tag in gps_info for tag in required_tags):
        print("[-] Координаты GPS неполные или повреждены.")
        return None
    lat = convert_to_degrees(gps_info["GPSLatitude"])
    if gps_info["GPSLatitudeRef"] != "N":
        lat = -lat
    lon = convert_to_degrees(gps_info["GPSLongitude"])
    if gps_info["GPSLongitudeRef"] != "E":
        lon = -lon
    return lat, lon

def create_map(lat, lon, output_map="photo_location.html"):
    # Новая стабильная подложка, которая не выдает ошибку 403
    my_map = folium.Map(location=[lat, lon], zoom_start=15, tiles="CartoDB positron")
    folium.Marker(
        [lat, lon],
        popup=f"<b>Фото сделано тут!</b><br>Широта: {lat:.5f}<br>Долгота: {lon:.5f}",
        icon=folium.Icon(color="red", icon="camera")
    ).add_to(my_map)
    my_map.save(output_map)
    print(f"[+] Интерактивная карта успешно создана: {output_map}")

def main():
    print("=" * 50)
    print(" 📸 EXIF-Машина: Поиск геолокации по фотографии 📸 ")
    print("=" * 50)
    image_path = input("[?] Введите путь к изображению (например, test.jpg): ").strip()
    if not os.path.exists(image_path):
        print("[-] Файл не найден. Проверьте путь.")
        return
    print("[*] Анализируем метаданные...")
    exif = get_exif_data(image_path)
    if exif:
        coords = get_gps_coordinates(exif)
        if coords:
            print(f"[+] Координаты найдены! Широта: {coords[0]}, Долгота: {coords[1]}")
            create_map(coords[0], coords[1])

if __name__ == "__main__":
    main()
