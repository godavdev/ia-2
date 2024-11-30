from pytubefix import YouTube
from pytubefix.cli import on_progress
from pytubefix.contrib.search import Search, Filter

SEARCHS = {
    "mazda3": "Mazda 3 2010 Commercial",
    "tsuru": "Nissan Tsuru 1993 Commercial",
    "vocho": "Volskwagen Sedan Vocho",
    "miata": "Mazda Miata 1990 Commercial",
    "mini": "mini cooper Commercial",
    # "dolphin": "BYD Dolphin 2024",
    # "corolla": "Toyota Corolla 2024",
    # "combi": "Volkswagen Combi",
}

# Descargar videos de youtube
for car, query in SEARCHS.items():
    results = Search(
        query, filters={"duration": Filter.get_duration("Under 4 minutes")}
    )
    while len(results.videos) < 20:
        results.get_next_results()

    print(f"Se han encontrado {len(results.videos)} videos para {car}")
    i = 0
    for result in results.videos:
        try:
            yt = YouTube(result.watch_url, on_progress_callback=on_progress)
            video = yt.streams.get_highest_resolution()
            print(f"Descargando video para {car}...")
            video.download(
                output_path=f"cnn/data/downloads/videos/{car}", filename=f"{i}.mp4"
            )
            i += 1
            print(f"Se ha descargado el video para {car}!")
        except:
            print(f"Error al descargar el video para {car}")
