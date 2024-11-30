import os
from bing_image_downloader import downloader

PATH = "cnn/data/downloads/images"

SEARCHS = {
    "Mazda 3 2010 Sedan exterior": "mazda3",
    "BYD Dolphin 2024 exterior": "dolphin",
    "Pagani huayra codalunga exterior": "pagani",
    "Volkswagen Combi exterior": "combi",
    "Toyota GR Supra 2025 exterior": "supra",
}
# Descargar imagenes de bing
for query, car in SEARCHS.items():
    downloader.download(
        query,
        limit=1000,
        # filter="photo",
        output_dir=f"{PATH}",
        adult_filter_off=True,
        force_replace=True,
        timeout=60,
        verbose=True,
    )

# Renombrar directorios
cars = os.listdir(PATH)
for car in cars:
    os.rename(f"{PATH}/{car}", f"{PATH}/{SEARCHS[car]}")

# Renombrar imagenes
cars = os.listdir(PATH)
for car in cars:
    images = os.listdir(f"{PATH}/{car}")
    i = 0
    for image in images:
        _, ext = os.path.splitext(image)
        os.rename(f"{PATH}/{car}/{image}", f"{PATH}/{car}/{i}{ext}")
        i += 1
