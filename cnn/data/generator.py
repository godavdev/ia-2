import os
from typing import Dict, List
from ultralytics import YOLO
import cv2


VIDEOS_DIR = "cnn/data/downloads/videos"
IMAGES_DIR = "cnn/data/images"

cars_dict: Dict[str, List[str]] = {}
cars = os.listdir(VIDEOS_DIR)
for car in cars:
    os.makedirs(f"{IMAGES_DIR}/{car}", exist_ok=True)
    car_dir = f"{VIDEOS_DIR}/{car}"
    videos = os.listdir(car_dir)
    cars_dict[car] = videos

model = YOLO("cnn/data/yolov8l.pt", verbose=False)
names = model.names
DIMENSIONS = (80, 80)
FRAME_INTERVAL = 10

for car, videos in cars_dict.items():
    # input(f"Presiona enter para procesar {car}")
    for video in videos:
        cap = cv2.VideoCapture(f"{VIDEOS_DIR}/{car}/{video}")
        i = 0
        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame_count += 1
            if frame_count % FRAME_INTERVAL != 0:
                continue
            results = model(frame, stream=True)
            for r in results:
                print(r)
                boxes = r.boxes
                for box in boxes:
                    name = model.names[int(box.cls[0])]
                    if box.conf[0] < 0.6 or (
                        name != "car" and name != "truck" and name != "bus"
                    ):
                        continue
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    w, h = x2 - x1, y2 - y1
                    cropped = frame[y1:y2, x1:x2]
                    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
                    resized = cv2.resize(gray, DIMENSIONS, interpolation=cv2.INTER_AREA)
                    cv2.imshow("Cropped", resized)
                    cv2.imwrite(f"cnn/data/images/{car}/{i}.jpg", resized)
                    i += 1
                    print(f"Teoricamente se han guardado: {i} imagenes")
            cv2.imshow("Frame", frame)
            cv2.waitKey(1)
        print("Finished")
