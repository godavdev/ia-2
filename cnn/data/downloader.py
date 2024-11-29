from pytubefix import YouTube
from pytubefix.cli import on_progress
from pytubefix.contrib.search import Search, Filter

SEARCHS = [
    ("mazda3", "Mazda 3 2010 Sedan"),
    ("dolphin", "BYD Dolphin 2024"),
    ("corolla", "Toyota Corolla 2024"),
    ("combi", "Volkswagen Combi"),
    ("vocho", "Volskwagen Sedan Vocho"),
]

for car, query in SEARCHS:
    results = Search(
        query, filters={"duration": Filter.get_duration("Under 4 minutes")}
    )
    results.get_next_results()
    results.get_next_results()
    print(f"Found {len(results.videos)} videos for {car}")
    i = 0
    for result in results.videos:
        try:
            yt = YouTube(result.watch_url, on_progress_callback=on_progress)
            video = yt.streams.get_highest_resolution()
            print(f"Downloading video for {car}...")
            video.download(output_path=f"cnn/data/videos/{car}", filename=f"{i}.mp4")
            i += 1
            print(f"Video for {car} downloaded successfully")
        except:
            print(f"Failed to download video for {car}")
