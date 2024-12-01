import os
from bing_image_downloader import downloader

PATH = "cnn/data/downloads/images"

SEARCHS = {
    # "mazda3": "Mazda 3 2010 Sedan",
    # "tsuru": "Nissan Tsuru 1993",
    "vocho": "Volskwagen Sedan Vocho",
    "miata": "Mazda Miata 1990",
    "mini": "Mini cooper",
}

# Descargar imagenes de bing
for car, query in SEARCHS.items():
    downloader.download(
        query,
        limit=1000,
        output_dir=f"{PATH}",
        # filter="photo",
        adult_filter_off=True,
        force_replace=True,
        timeout=5,
        verbose=True,
    )

# Renombrar directorios
for car, query in SEARCHS.items():
    os.rename(f"{PATH}/{query}", f"{PATH}/{car}")


# Renombrar imagenes
cars = os.listdir(PATH)
for car in cars:
    images = os.listdir(f"{PATH}/{car}")
    i = 0
    for image in images:
        _, ext = os.path.splitext(image)
        os.rename(f"{PATH}/{car}/{image}", f"{PATH}/{car}/{i}{ext}")
        i += 1
